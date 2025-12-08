# ============================================================
# PyTab - Módulo de Agregação Temporal
# ============================================================
# Responsável por:
# - Detectar a coluna de data
# - Ordenar série temporal
# - Agregar dados automaticamente (dia, semana, mês, trimestre, ano)
# - Calcular média móvel opcional
# - Converter tudo para um formato uniforme e seguro
# ============================================================

import pandas as pd


# ------------------------------------------------------------
# Tabela de equivalência dos períodos
# ------------------------------------------------------------
PERIOD_MAP = {
    "Diário": "D",
    "Semanal": "W",
    "Mensal": "M",
    "Trimestral": "Q",
    "Anual": "Y",
}


# ------------------------------------------------------------
# Detecta a coluna de data automaticamente
# ------------------------------------------------------------
def detect_date_column(df: pd.DataFrame):
    """
    Retorna a primeira coluna de datas encontrada.
    Se não houver, retorna None.
    """

    # 1) Colunas já convertidas para datetime
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    if date_cols:
        return date_cols[0]

    # 2) Tenta converter colunas que parecem datas
    for col in df.columns:
        try:
            converted = pd.to_datetime(df[col], errors="raise")
            return col
        except Exception:
            continue

    return None


# ------------------------------------------------------------
# Agrega série temporal por período (dia / semana / mês…)
# ------------------------------------------------------------
def aggregate_series(df: pd.DataFrame, date_col: str, indicador: str, periodo: str):
    """
    Agrega uma coluna numérica por período usando resample().
    """

    if periodo not in PERIOD_MAP:
        raise ValueError(f"Período inválido: {periodo}")

    rule = PERIOD_MAP[periodo]

    df2 = df.copy()
    df2[date_col] = pd.to_datetime(df2[date_col], errors="coerce")

    df2 = df2.dropna(subset=[date_col])  # elimina datas inválidas
    df2 = df2.sort_values(by=date_col).set_index(date_col)

    serie = df2[indicador].resample(rule).mean().dropna()

    return serie


# ------------------------------------------------------------
# Calcula série temporal + média móvel (opcional)
# ------------------------------------------------------------
def compute_trend(serie: pd.Series, janela_mm: int | None = None):
    """
    Retorna:
    - série original
    - série de média móvel (se requerida)
    """

    if janela_mm is None:
        return serie, None

    rolling = serie.rolling(janela_mm, min_periods=1).mean()
    return serie, rolling


