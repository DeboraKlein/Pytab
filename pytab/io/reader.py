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
import pandas as pd


def read_csv_smart(path: str) -> pd.DataFrame:
    """
    Leitura robusta de CSV, testando separadores e encodings comuns.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    attempts = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": "\t", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin-1"},
        {"sep": ";", "encoding": "latin-1"},
        {"sep": "\t", "encoding": "latin-1"},
    ]

    last_error = None

    for cfg in attempts:
        try:
            df = pd.read_csv(
                path,
                sep=cfg["sep"],
                encoding=cfg["encoding"],
                engine="python"
            )
            if df.shape[1] > 0:  # Verifica se carregou alguma coluna
                return df
        except Exception as e:
            last_error = e
            continue


    raise ValueError(f"Falha ao ler CSV. Último erro: {last_error}")


def read_excel_smart(path: str) -> pd.DataFrame:
    """
    Leitura de arquivos Excel (.xlsx) usando o engine openpyxl.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return pd.read_excel(path, engine="openpyxl")


def read_any(path: str) -> pd.DataFrame:
    """
    Função de alto nível para ler qualquer arquivo suportado.

    Suportado:
    - .csv
    - .txt
    - .xlsx
    """
    ext = os.path.splitext(path)[1].lower()

    if ext in [".csv", ".txt"]:
        return read_csv_smart(path)

    if ext in [".xlsx"]:
        return read_excel_smart(path)

    raise ValueError(f"Formato de arquivo não suportado: {ext}")
