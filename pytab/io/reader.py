"""
pytab.io.reader
----------------
Módulo responsável por leitura robusta de arquivos CSV e Excel.

Funções principais:
- read_csv_smart: tenta diferentes separadores e encodings.
- read_excel_smart: leitura padrão de XLSX.
- read_any: identifica o tipo do arquivo e chama o leitor correto.
"""

import os
from pathlib import Path
from typing import Union, Optional

import pandas as pd

PathLike = Union[str, os.PathLike]


def _ensure_exists(path: PathLike) -> str:
    """
    Garante que o arquivo existe e devolve o caminho como string.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {p}")
    return str(p)


def read_csv_smart(path: PathLike) -> pd.DataFrame:
    """
    Leitura robusta de CSV/TXT, testando separadores e encodings comuns.

    Tenta combinações de:
      - separadores: ',', ';', '\\t'
      - encodings: 'utf-8', 'latin-1'

    Lança ValueError se todas as tentativas falharem.
    """
    path_str = _ensure_exists(path)

    attempts = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": "\t", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin-1"},
        {"sep": ";", "encoding": "latin-1"},
        {"sep": "\t", "encoding": "latin-1"},
    ]

    last_error: Optional[Exception] = None

    for cfg in attempts:
        try:
            df = pd.read_csv(
                path_str,
                sep=cfg["sep"],
                encoding=cfg["encoding"],
                engine="python",     # evitar problemas com low_memory e separador
            )
            # Se carregou pelo menos 1 coluna, consideramos válido
            if df.shape[1] > 0:
                return df
        except Exception as e:
            last_error = e
            continue

    raise ValueError(f"Falha ao ler CSV. Último erro: {last_error}")


def read_excel_smart(
    path: PathLike,
    sheet_name: Union[int, str, None] = 0,
) -> pd.DataFrame:
    """
    Leitura simples de arquivos Excel (.xlsx, .xlsm).

    Parâmetros:
      - path: caminho do arquivo
      - sheet_name:
          0 (default) -> primeira aba
          nome da aba -> 'Planilha1', etc.
          None -> tenta ler todas as abas (retorna dict de DataFrames)

    Observação:
      É necessário ter 'openpyxl' instalado para ler .xlsx com pandas.
      Se der erro de engine, instale com:

          pip install openpyxl
    """
    path_str = _ensure_exists(path)

    try:
        df = pd.read_excel(path_str, sheet_name=sheet_name)
        return df
    except ImportError as e:
        raise ImportError(
            "Falha ao ler Excel. Verifique se o pacote 'openpyxl' está instalado "
            "(ex: pip install openpyxl)."
        ) from e
    except Exception as e:
        raise ValueError(f"Falha ao ler Excel: {e}") from e


def read_any(path: PathLike) -> pd.DataFrame:
    """
    Leitor genérico que escolhe a função correta com base na extensão.

    Suportado:
      - .csv
      - .txt
      - .xlsx
      - .xlsm
    """
    path_str = _ensure_exists(path)
    ext = Path(path_str).suffix.lower()

    if ext in [".csv", ".txt"]:
        return read_csv_smart(path_str)

    if ext in [".xlsx", ".xlsm"]:
        return read_excel_smart(path_str)

    raise ValueError(f"Formato de arquivo não suportado: {ext}")
