"""
pytab.stats.descriptive
-----------------------
Funções de estatística descritiva para DataFrames.
"""

import pandas as pd


def summarize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera estatísticas descritivas para colunas numéricas de um DataFrame.

    Retorna um DataFrame com:
        - count: número de valores não nulos
        - missing: número de valores nulos
        - mean: média
        - std: desvio padrão
        - min: mínimo
        - q1: 1º quartil (25%)
        - median: mediana
        - q3: 3º quartil (75%)
        - max: máximo
        - cv: coeficiente de variação (std / mean)

    Se não houver colunas numéricas, retorna DataFrame vazio.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return pd.DataFrame()

    desc = numeric_df.describe(percentiles=[0.25, 0.5, 0.75]).T

    # Renomeia colunas para nomes mais claros
    desc = desc.rename(
        columns={
            "count": "count",
            "mean": "mean",
            "std": "std",
            "min": "min",
            "25%": "q1",
            "50%": "median",
            "75%": "q3",
            "max": "max",
        }
    )

    # Calcula missing e coeficiente de variação
    desc["missing"] = numeric_df.isna().sum()
    desc["cv"] = desc["std"] / desc["mean"]

    # Reordena colunas
    cols = [
        "count",
        "missing",
        "mean",
        "std",
        "cv",
        "min",
        "q1",
        "median",
        "q3",
        "max",
    ]
    desc = desc[cols]

    # Opcional: arredondar
    desc = desc.round(4)

    return desc
