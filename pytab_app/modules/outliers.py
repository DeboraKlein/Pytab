# ============================================================
# PyTab - Módulo de Outliers (backend, sem Streamlit)
# ============================================================
# Métodos suportados:
#  - Z-score
#  - IQR (Interquartile Range)
#  - MAD (Median Absolute Deviation)
#  - Modo automático: escolhe o melhor método com base nos dados
# ============================================================

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Literal, Tuple, Dict, Any

OutlierMethod = Literal["zscore", "iqr", "mad"]


# ------------------------------------------------------------
# Funções de detecção específicas
# ------------------------------------------------------------
def _detect_zscore(series: pd.Series, z_lim: float = 2.5) -> pd.DataFrame:
    s = series.astype(float)
    mean = s.mean()
    std = s.std(ddof=1)

    if std == 0 or np.isnan(std):
        z = pd.Series(np.nan, index=s.index)
        mask = pd.Series(False, index=s.index)
    else:
        z = (s - mean) / std
        mask = z.abs() > z_lim

    return pd.DataFrame(
        {
            "valor": s,
            "score": z,
            "outlier": mask,
        },
        index=s.index,
    )


def _detect_iqr(series: pd.Series, k: float = 1.5) -> pd.DataFrame:
    s = series.astype(float)
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - k * iqr
    upper = q3 + k * iqr

    mask = (s < lower) | (s > upper)

    # score: o quanto ultrapassou o limite normalizado pelo IQR
    score = pd.Series(0.0, index=s.index, dtype=float)
    score[mask & (s > upper)] = (s[mask & (s > upper)] - upper) / (iqr if iqr != 0 else 1)
    score[mask & (s < lower)] = (lower - s[mask & (s < lower)]) / (iqr if iqr != 0 else 1)

    return pd.DataFrame(
        {
            "valor": s,
            "score": score,
            "outlier": mask,
        },
        index=s.index,
    )


def _detect_mad(series: pd.Series, thresh: float = 3.5) -> pd.DataFrame:
    s = series.astype(float)
    median = s.median()
    abs_dev = (s - median).abs()
    mad = abs_dev.median()

    if mad == 0 or np.isnan(mad):
        z_mad = pd.Series(np.nan, index=s.index)
        mask = pd.Series(False, index=s.index)
    else:
        z_mad = 0.6745 * (s - median) / mad
        mask = z_mad.abs() > thresh

    return pd.DataFrame(
        {
            "valor": s,
            "score": z_mad,
            "outlier": mask,
        },
        index=s.index,
    )


# ------------------------------------------------------------
# Escolha automática de método
# ------------------------------------------------------------
def suggest_outlier_method(series: pd.Series) -> Tuple[OutlierMethod, str]:
    """
    Sugere o melhor método com base em:
    - tamanho da amostra
    - assimetria (skewness)
    """

    s = series.dropna().astype(float)
    n = len(s)

    if n == 0:
        return "zscore", "Série vazia. Usando Z-score por padrão."

    if n < 20:
        return "iqr", "Amostra pequena (< 20 valores). IQR é mais estável nesse caso."

    skew = s.skew()

    if not np.isfinite(skew):
        return "zscore", "Não foi possível calcular skewness. Usando Z-score como padrão."

    if abs(skew) <= 0.7:
        return "zscore", f"Distribuição aproximadamente simétrica (skewness = {skew:.2f}). Z-score é adequado."
    elif abs(skew) <= 2.0:
        return "iqr", f"Distribuição levemente assimétrica (skewness = {skew:.2f}). IQR é mais robusto."
    else:
        return "mad", f"Distribuição fortemente assimétrica (skewness = {skew:.2f}). MAD é o método mais robusto."


# ------------------------------------------------------------
# Função única de detecção (público)
# ------------------------------------------------------------
def detect_outliers(
    series: pd.Series,
    method: str = "auto",
    z_lim: float = 2.5,
    iqr_k: float = 1.5,
    mad_thresh: float = 3.5,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Detecta outliers em uma série numérica.

    Retorna:
      - DataFrame com colunas: valor, score, outlier, method
      - dict com metadados (método usado, parâmetros, mensagem explicativa)
    """

    s = series.astype(float)

    auto_msg = ""
    method_used: OutlierMethod

    if method == "auto":
        method_used, auto_msg = suggest_outlier_method(s)
    else:
        method = method.lower()
        if method not in ("zscore", "iqr", "mad"):
            method_used, auto_msg = suggest_outlier_method(s)
        else:
            method_used = method  # type: ignore

    if method_used == "zscore":
        df_res = _detect_zscore(s, z_lim)
        params = {"z_lim": z_lim}
    elif method_used == "iqr":
        df_res = _detect_iqr(s, iqr_k)
        params = {"k": iqr_k}
    else:  # "mad"
        df_res = _detect_mad(s, mad_thresh)
        params = {"thresh": mad_thresh}

    df_res["method"] = method_used

    info: Dict[str, Any] = {
        "method": method_used,
        "auto_message": auto_msg,
        "params": params,
        "n": int(len(s)),
        "n_outliers": int(df_res["outlier"].sum()),
    }

    return df_res, info
