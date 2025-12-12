import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pytab.charts.theme import PRIMARY, SECONDARY
from .regras import (
    regra_ponto_fora_limite,
    regra_tendencia,
    regra_lado_media,
)


# ======================================================================
# CARTA I-MR
# ======================================================================


def carta_imr(serie: pd.Series):
    """
    Carta I-MR (Individuais e Amplitude Móvel)

    Parâmetros
    ----------
    serie : pd.Series
        Série numérica com os dados individuais, em ordem temporal.

    Retorno
    -------
    fig : matplotlib.figure.Figure
    resumo : dict
        Dicionário com média, sigma, limites de controle e contagem de violações.
    """
    dados = (
        pd.Series(serie)
        .dropna()
        .astype(float)
        .reset_index(drop=True)
    )
    n = len(dados)
    if n < 5:
        raise ValueError("Poucos pontos para carta I-MR (mínimo recomendado: 5).")

    # Estatísticas básicas
    mean = dados.mean()
    sigma = dados.std(ddof=1)

    # Limites de controle clássicos 3-sigma
    ucl = mean + 3 * sigma
    lcl = mean - 3 * sigma

    # MR (média da amplitude móvel de ordem 2)
    mr = dados.diff().abs().dropna()
    mr_bar = mr.mean() if len(mr) > 0 else 0.0

    # Constante d2 para n = 2
    d2 = 1.128
    sigma_est = mr_bar / d2 if d2 != 0 else 0.0

    # Limites da carta MR
    ucl_mr = mr_bar * 3.267 if mr_bar > 0 else 0.0
    lcl_mr = 0.0

    # Aplicação das regras (no gráfico I)
    viol1 = regra_ponto_fora_limite(dados, lcl, ucl)
    viol2 = regra_tendencia(dados)
    viol3 = regra_lado_media(dados)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    x = np.arange(n)

    # Gráfico I
    ax1.plot(x, dados, marker="o", linestyle="-", color=PRIMARY, label="Valor individual")
    ax1.axhline(mean, color="gray", linestyle="--", label="Média")
    ax1.axhline(ucl, color="red", linestyle="--", label="UCL")
    ax1.axhline(lcl, color="red", linestyle="--", label="LCL")

    if not viol1.empty:
        ax1.scatter(
            viol1["index"],
            dados.iloc[viol1["index"]],
            color="red",
            zorder=5,
            label="Pontos fora de controle",
        )

    ax1.set_title("Carta I (Individuais)")
    ax1.set_ylabel("Valor")
    ax1.legend(loc="best")

    # Gráfico MR
    x_mr = np.arange(1, n)
    ax2.plot(x_mr, mr.values, marker="o", linestyle="-", color=SECONDARY, label="MR")
    if mr_bar > 0:
        ax2.axhline(mr_bar, color="gray", linestyle="--", label="MR médio")
        ax2.axhline(ucl_mr, color="red", linestyle="--", label="UCL MR")
        ax2.axhline(lcl_mr, color="red", linestyle="--", label="LCL MR")

    ax2.set_title("Carta MR (Amplitude Móvel)")
    ax2.set_xlabel("Ordem")
    ax2.set_ylabel("Amplitude")
    ax2.legend(loc="best")

    plt.tight_layout()

    resumo = {
        "media": float(mean),
        "ucl": float(ucl),
        "lcl": float(lcl),
        "sigma": float(sigma),
        "mr_bar": float(mr_bar),
        "ucl_mr": float(ucl_mr),
        "lcl_mr": float(lcl_mr),
        "sigma_est": float(sigma_est),
        "violacoes_regra1": int(len(viol1)),
        "violacoes_regra2": int(len(viol2)),
        "violacoes_regra3": int(len(viol3)),
    }

    return fig, resumo


# ======================================================================
# CARTA XBAR-R
# ======================================================================

_A2 = {2: 1.88, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483}
_D3 = {2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}
_D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004}


def _split_subgrupos(dados: pd.Series, n_subgrupo: int) -> np.ndarray:
    valores = (
        pd.Series(dados)
        .dropna()
        .astype(float)
        .to_numpy()
    )
    n = len(valores)
    k = n // n_subgrupo
    if k == 0:
        raise ValueError("Poucos pontos para formar subgrupos com esse tamanho.")
    valores = valores[: k * n_subgrupo]
    return valores.reshape(k, n_subgrupo)


def carta_xbar_r(serie: pd.Series, n_subgrupo: int):
    """
    Carta X̄-R para dados contínuos agrupados em subgrupos de mesmo tamanho.
    """
    if n_subgrupo not in _A2:
        raise ValueError("Tamanho de subgrupo suportado: 2 a 6.")

    matriz = _split_subgrupos(serie, n_subgrupo)
    medias = matriz.mean(axis=1)
    ranges = matriz.max(axis=1) - matriz.min(axis=1)

    xbar = medias.mean()
    rbar = ranges.mean()

    A2 = _A2[n_subgrupo]
    D3 = _D3[n_subgrupo]
    D4 = _D4[n_subgrupo]

    ucl_x = xbar + A2 * rbar
    lcl_x = xbar - A2 * rbar

    ucl_r = D4 * rbar
    lcl_r = D3 * rbar

    idx = np.arange(1, len(medias) + 1)

    viol1_x = regra_ponto_fora_limite(medias, lcl_x, ucl_x)
    viol1_r = regra_ponto_fora_limite(ranges, lcl_r, ucl_r)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # X̄
    ax1.plot(idx, medias, marker="o", linestyle="-", color=PRIMARY)
    ax1.axhline(xbar, color="gray", linestyle="--", label="Média")
    ax1.axhline(ucl_x, color="red", linestyle="--", label="UCL")
    ax1.axhline(lcl_x, color="red", linestyle="--", label="LCL")

    if not viol1_x.empty:
        ax1.scatter(
            viol1_x["index"] + 1,
            medias[viol1_x["index"]],
            color="red",
            zorder=5,
            label="Fora de controle",
        )

    ax1.set_title("Carta X̄")
    ax1.set_ylabel("Média")

    # R
    ax2.plot(idx, ranges, marker="o", linestyle="-", color=SECONDARY)
    ax2.axhline(rbar, color="gray", linestyle="--", label="R médio")
    ax2.axhline(ucl_r, color="red", linestyle="--", label="UCL")
    ax2.axhline(lcl_r, color="red", linestyle="--", label="LCL")

    if not viol1_r.empty:
        ax2.scatter(
            viol1_r["index"] + 1,
            ranges[viol1_r["index"]],
            color="red",
            zorder=5,
            label="Fora de controle",
        )

    ax2.set_title("Carta R")
    ax2.set_xlabel("Subgrupo")
    ax2.set_ylabel("Amplitude")
    ax2.legend(loc="best")

    plt.tight_layout()

    resumo = {
        "xbar": float(xbar),
        "rbar": float(rbar),
        "ucl_x": float(ucl_x),
        "lcl_x": float(lcl_x),
        "ucl_r": float(ucl_r),
        "lcl_r": float(lcl_r),
        "violacoes_x": int(len(viol1_x)),
        "violacoes_r": int(len(viol1_r)),
        "n_subgrupo": int(n_subgrupo),
    }

    return fig, resumo


# ======================================================================
# CARTA P (PROPORÇÃO DE DEFEITUOSOS)
# ======================================================================


def carta_p(defeituosos: pd.Series, inspecionados: pd.Series):
    """
    Carta P: proporção de itens defeituosos em cada amostra.

    defeituosos: número de itens defeituosos por amostra
    inspecionados: total de itens inspecionados por amostra
    """
    d = pd.Series(defeituosos).astype(float)
    n = pd.Series(inspecionados).astype(float)

    mask = (n > 0) & d.notna() & n.notna()
    d = d[mask]
    n = n[mask]

    if len(d) < 5:
        raise ValueError("Poucos pontos para carta P (mínimo recomendado: 5).")

    p = d / n
    p_bar = d.sum() / n.sum()

    # Evitar problemas quando p_bar é 0 ou 1
    if p_bar <= 0 or p_bar >= 1:
        raise ValueError(
            "Proporção média de defeituosos é 0 ou 1; carta P não é apropriada para este caso."
        )

    sigma_p = np.sqrt(p_bar * (1 - p_bar) / n)
    ucl = p_bar + 3 * sigma_p
    lcl = p_bar - 3 * sigma_p
    lcl = np.maximum(lcl, 0.0)

    idx = np.arange(1, len(p) + 1)

    viol = regra_ponto_fora_limite(p, lcl, ucl)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(idx, p, marker="o", linestyle="-", color=PRIMARY, label="p (amostral)")
    ax.axhline(p_bar, color="gray", linestyle="--", label="p̄ (média)")

    ax.plot(idx, ucl, color="red", linestyle="--", label="UCL")
    ax.plot(idx, lcl, color="red", linestyle="--", label="LCL")

    if not viol.empty:
        ax.scatter(
            viol["index"] + 1,
            p.iloc[viol["index"]],
            color="red",
            zorder=5,
            label="Fora de controle",
        )

    ax.set_title("Carta P (proporção de defeituosos)")
    ax.set_xlabel("Amostra")
    ax.set_ylabel("Proporção defeituosa")
    ax.legend(loc="best")
    plt.tight_layout()

    resumo = {
        "p_bar": float(p_bar),
        "violacoes": int(len(viol)),
    }

    return fig, resumo


# ======================================================================
# CARTA U (DEFEITOS POR UNIDADE)
# ======================================================================


def carta_u(defeitos: pd.Series, oportunidades: pd.Series):
    """
    Carta U: defeitos por unidade de oportunidade.

    defeitos: número de defeitos observados por amostra
    oportunidades: número de unidades de oportunidade na amostra
    """
    d = pd.Series(defeitos).astype(float)
    n = pd.Series(oportunidades).astype(float)

    mask = (n > 0) & d.notna() & n.notna()
    d = d[mask]
    n = n[mask]

    if len(d) < 5:
        raise ValueError("Poucos pontos para carta U (mínimo recomendado: 5).")

    u = d / n
    u_bar = d.sum() / n.sum()

    if u_bar < 0:
        raise ValueError("Média de defeitos por unidade inválida (negativa).")

    sigma_u = np.sqrt(u_bar / n)
    ucl = u_bar + 3 * sigma_u
    lcl = u_bar - 3 * sigma_u
    lcl = np.maximum(lcl, 0.0)

    idx = np.arange(1, len(u) + 1)

    viol = regra_ponto_fora_limite(u, lcl, ucl)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(idx, u, marker="o", linestyle="-", color=PRIMARY, label="u (amostral)")
    ax.axhline(u_bar, color="gray", linestyle="--", label="ū (média)")

    ax.plot(idx, ucl, color="red", linestyle="--", label="UCL")
    ax.plot(idx, lcl, color="red", linestyle="--", label="LCL")

    if not viol.empty:
        ax.scatter(
            viol["index"] + 1,
            u.iloc[viol["index"]],
            color="red",
            zorder=5,
            label="Fora de controle",
        )

    ax.set_title("Carta U (defeitos por unidade de oportunidade)")
    ax.set_xlabel("Amostra")
    ax.set_ylabel("Defeitos por unidade")
    ax.legend(loc="best")
    plt.tight_layout()

    resumo = {
        "u_bar": float(u_bar),
        "violacoes": int(len(viol)),
    }

    return fig, resumo
