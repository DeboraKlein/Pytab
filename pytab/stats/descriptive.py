import pandas as pd

def summarize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna estatísticas descritivas básicas para todas as colunas numéricas.
    """
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return pd.DataFrame()

    desc = numeric_df.describe().T
    desc["missing"] = numeric_df.isna().sum()
    return desc
