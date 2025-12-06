"""
pytab.stats.outliers
--------------------
Funções para cálculo de z-score e detecção de outliers.
"""

from typing import Literal, Dict, Any

import numpy as np
import pandas as pd


def zscore_series(
    s: pd.Series,
    ddof: int = 0
) -> pd.Series:
    """
    Calcula o z-score de uma série numérica.

    z = (x - média) / desvio_padrão

    ddof:
        0 -> desvio populacional
        1 -> desvio amostral
    """
    s = pd.to_numeric(s, errors="coerce")

    mean = s.mean()
    std = s.std(ddof=ddof)

    if std == 0 or np.isnan(std):
        # Tudo igual ou série vazia: z-score não faz sentido
        return pd.Series(np.nan, index=s.index, name="zscore")

    z = (s - mean) / std
    z.name = "zscore"
    return z


def detect_outliers_zscore(
    s: pd.Series,
    threshold: float = 3.0,
    ddof: int = 0
) -> Dict[str, Any]:
    """
    Detecta outliers em uma série numérica usando z-score.

    threshold:
        valor absoluto mínimo de |z| para considerar outlier (default = 3.0)

    Retorna um dicionário com:
        - zscore: Series de z-scores
        - mask: Series booleana (True = outlier)
        - outliers: DataFrame com índice original, valor e z-score
        - summary: dict com resumo (n, n_outliers, pct_outliers, threshold)
    """
    z = zscore_series(s, ddof=ddof)
    mask = z.abs() >= threshold

    outliers_df = pd.DataFrame({
        "value": s,
        "zscore": z,
    }).loc[mask]

    n = s.notna().sum()
    n_out = mask.sum()
    pct_out = (n_out / n * 100) if n > 0 else 0.0

    summary = {
        "n": int(n),
        "n_outliers": int(n_out),
        "pct_outliers": round(pct_out, 2),
        "threshold": threshold,
    }

    return {
        "zscore": z,
        "mask": mask,
        "outliers": outliers_df,
        "summary": summary,
    }


def detect_outliers_iqr(
    s: pd.Series,
    factor: float = 1.5
) -> Dict[str, Any]:
    """
    Detecta outliers usando o método do IQR (Interquartile Range).

    Regra clássica:
      - limite_inferior = Q1 - factor * IQR
      - limite_superior = Q3 + factor * IQR

    Retorna um dicionário com:
        - mask: Series booleana (True = outlier)
        - outliers: DataFrame com índice original, valor, limites e IQR
        - bounds: dict com q1, q3, iqr, lower, upper
        - summary: dict com n, n_outliers, pct_outliers, factor
    """
    s = pd.to_numeric(s, errors="coerce")
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1

    if pd.isna(iqr) or iqr == 0:
        mask = pd.Series(False, index=s.index)
        bounds = {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower": q1,
            "upper": q3,
        }
        return {
            "mask": mask,
            "outliers": pd.DataFrame(columns=["value"]),
            "bounds": bounds,
            "summary": {
                "n": int(s.notna().sum()),
                "n_outliers": 0,
                "pct_outliers": 0.0,
                "factor": factor,
            },
        }

    lower = q1 - factor * iqr
    upper = q3 + factor * iqr

    mask = (s < lower) | (s > upper)

    outliers_df = pd.DataFrame({
        "value": s,
    }).loc[mask]

    n = s.notna().sum()
    n_out = mask.sum()
    pct_out = (n_out / n * 100) if n > 0 else 0.0

    bounds = {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower": lower,
        "upper": upper,
    }

    summary = {
        "n": int(n),
        "n_outliers": int(n_out),
        "pct_outliers": round(pct_out, 2),
        "factor": factor,
    }

    return {
        "mask": mask,
        "outliers": outliers_df,
        "bounds": bounds,
        "summary": summary,
    }


def detect_outliers(
    s: pd.Series,
    method: Literal["zscore", "iqr"] = "zscore",
    threshold: float = 3.0,
    factor: float = 1.5,
    ddof: int = 0,
) -> Dict[str, Any]:
    """
    Função de alto nível para detecção de outliers em uma série.

    method:
        - "zscore": usa detect_outliers_zscore
        - "iqr": usa detect_outliers_iqr
    """
    if method == "zscore":
        return detect_outliers_zscore(s, threshold=threshold, ddof=ddof)
    elif method == "iqr":
        return detect_outliers_iqr(s, factor=factor)
    else:
        raise ValueError(f"Método de outlier não suportado: {method}")
