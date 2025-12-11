import pandas as pd


def calcular_gap(serie: pd.Series, meta: float):
    atual = serie.mean()
    gap = atual - meta
    return atual, gap


def simular_cenarios(serie: pd.Series, reducao_pct: float):
    fator = 1 - reducao_pct / 100
    sim = serie * fator
    return pd.DataFrame({
        "Valor Original": serie,
        f"Simulado (-{reducao_pct}%)": sim
    })
