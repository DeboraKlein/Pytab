"""
pytab_app.modules.aggregation
-----------------------------

- detect_date_column(df): tenta sugerir uma coluna de data mesmo quando vem como object.
- aggregate_series(df, date_col, indicador, periodicidade): agrega série temporal de forma robusta.

Objetivo: não quebrar o app por problemas de schema / parsing.
"""

from __future__ import annotations

import pandas as pd


_PERIODICITY_TO_RULE = {
    "Diário": "D",
    "Semanal": "W",
    "Mensal": "MS",
    "Trimestral": "QS",
    "Anual": "YS",
}


def detect_date_column(df: pd.DataFrame) -> str | None:
    """
    Heurística simples e robusta:
    1) Se houver datetime dtype, escolhe a primeira.
    2) Caso contrário, tenta parsear colunas object e pega a que tiver maior taxa de parse válido.
    """
    # 1) datetime nativo
    dt_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]", "datetimetz"]).columns.tolist()
    if dt_cols:
        return dt_cols[0]

    # 2) tentar parsear object
    best_col = None
    best_ratio = 0.0

    obj_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    for c in obj_cols:
        s = df[c]
        # tenta parsear; coerção para NaT em inválidos
        parsed = pd.to_datetime(s, errors="coerce", infer_datetime_format=True)
        ratio = parsed.notna().mean() if len(parsed) else 0.0
        if ratio > best_ratio and ratio >= 0.6:  # limiar conservador
            best_ratio = ratio
            best_col = c

    return best_col


def aggregate_series(
    df: pd.DataFrame,
    date_col: str,
    indicador: str,
    periodicidade: str,
) -> pd.DataFrame:
    """
    Retorna DataFrame agregado com colunas:
        - date (index temporal)
        - <indicador> (média no período)

    Lança ValueError com mensagem clara se colunas não existirem.
    """
    if date_col not in df.columns:
        raise ValueError(f"Coluna de data '{date_col}' não existe no DataFrame.")

    if indicador not in df.columns:
        raise ValueError(f"Indicador '{indicador}' não existe no DataFrame.")

    rule = _PERIODICITY_TO_RULE.get(periodicidade)
    if rule is None:
        raise ValueError(f"Periodicidade inválida: {periodicidade}")

    # manter SOMENTE as duas colunas necessárias (isso evita efeitos colaterais)
    df2 = df[[date_col, indicador]].copy()

    # parse robusto de datas
    df2[date_col] = pd.to_datetime(df2[date_col], errors="coerce", infer_datetime_format=True)

    # remover linhas sem data ou sem indicador
    df2 = df2.dropna(subset=[date_col, indicador])

    if df2.empty:
        # retorna vazio padronizado para a UI decidir o que fazer
        return pd.DataFrame(columns=[date_col, indicador])

    # set index e resample
    df2 = df2.set_index(date_col).sort_index()

    serie = df2[indicador].resample(rule).mean().dropna()

    out = serie.reset_index()
    out.columns = [date_col, indicador]
    return out

