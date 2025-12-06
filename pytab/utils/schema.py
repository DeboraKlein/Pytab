"""
pytab.utils.schema
------------------
Funções utilitárias para detectar tipos de colunas
e estruturar metadados do DataFrame.
"""

import pandas as pd


def detect_column_types(df: pd.DataFrame) -> dict:
    """
    Detecta grupos de colunas por tipo.

    Retorna:
        {
            "numeric": [...],
            "categorical": [...],
            "datetime": [...]
        }
    """

    numeric = df.select_dtypes(include="number").columns.tolist()
    datetime = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # Candidatas a categóricas = não numéricas e não datas
    categorical = [
        col for col in df.columns if col not in numeric and col not in datetime
    ]

    return {
        "numeric": numeric,
        "categorical": categorical,
        "datetime": datetime,
    }
