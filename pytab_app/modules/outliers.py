"""
Módulo de detecção de outliers para o PyTab.
Suporta: Z-score, IQR e MAD.
"""

import numpy as np
import pandas as pd


def zscore_outliers(series: pd.Series, threshold=3):
    s = series.dropna()
    z = (s - s.mean()) / s.std(ddof=1)
    mask = np.abs(z) > threshold
    return s[mask], z


def iqr_outliers(series: pd.Series, multiplier=1.5):
    s = series.dropna()
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    mask = (s < lower) | (s > upper)
    return s[mask], (lower, upper)


def mad_outliers(series: pd.Series, threshold=3.5):
    s = series.dropna()
    median = s.median()
    mad = np.median(np.abs(s - median))
    modified_z = 0.6745 * (s - median) / mad if mad != 0 else np.zeros(len(s))
    mask = np.abs(modified_z) > threshold
    return s[mask], modified_z


def detectar_outliers(series: pd.Series, metodo="Auto"):
    """
    Detecta outliers de forma automática ou conforme método selecionado.
    """
    if metodo == "Z-score":
        return zscore_outliers(series)

    if metodo == "IQR":
        return iqr_outliers(series)

    if metodo == "MAD":
        return mad_outliers(series)

    # ---- Automático ----
    s = series.dropna()
    cv = s.std(ddof=1) / s.mean()

    if cv < 0.10:
        return iqr_outliers(s)
    elif cv < 0.30:
        return zscore_outliers(s, threshold=2.5)
    else:
        return mad_outliers(s)
