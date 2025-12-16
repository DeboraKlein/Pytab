from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import plotly.graph_objects as go

from patsy.builtins import Q  # lida com nomes de colunas com espaço/caracteres especiais
from pytab.charts.theme import PRIMARY, SECONDARY


# ============================================================
# Helpers (formatação para usuário final)
# ============================================================

def _fmt_num_user(x: float | None, nd: int = 2) -> str:
    if x is None:
        return "-"
    try:
        x = float(x)
    except Exception:
        return "-"
    if np.isnan(x):
        return "-"
    return f"{x:.{nd}f}".replace(".", ",")


def _fmt_p_user(p: float | None) -> str:
    """Sem notação científica; evita '0.0000' e torna leitura imediata."""
    if p is None:
        return "-"
    try:
        p = float(p)
    except Exception:
        return "-"
    if np.isnan(p):
        return "-"
    if p < 0.0001:
        return "< 0,0001"
    return f"{p:.4f}".replace(".", ",")


# ============================================================
# Contrato estatístico base (para validação automática)
# ============================================================

def _base_contract(
    *,
    teste: str,
    n: int,
    mean: float | None,
    std: float | None,
    t_stat: float | None = None,
    f_stat: float | None = None,
    p_value: float | None = None,
    **extra,
) -> dict:
    """Garante presença do contrato base; permite extras."""
    out = {
        "teste": str(teste),
        "n": int(n),
        "mean": None if mean is None else float(mean),
        "std": None if std is None else float(std),
        "t_stat": None if t_stat is None else float(t_stat),
        "f_stat": None if f_stat is None else float(f_stat),
        "p_value": None if p_value is None else float(p_value),
    }
    out.update(extra)
    return out


# ============================================================
# 1) TESTES t
# ============================================================

def teste_t_uma_amostra(serie: pd.Series, mu0: float) -> dict:
    serie = serie.dropna()
    n = int(len(serie))

    mean = float(serie.mean()) if n else None
    std = float(serie.std(ddof=1)) if n > 1 else None

    t_stat, p_value = (np.nan, np.nan)
    if n >= 2:
        t_stat, p_value = stats.ttest_1samp(serie, popmean=float(mu0))

    return _base_contract(
        teste="t_test_one_sample",
        n=n,
        mean=mean,
        std=std,
        t_stat=None if np.isnan(t_stat) else float(t_stat),
        f_stat=None,
        p_value=None if np.isnan(p_value) else float(p_value),
        mu0=float(mu0),
    )


def teste_t_duas_amostras(g1: pd.Series, g2: pd.Series) -> dict:
    g1 = g1.dropna()
    g2 = g2.dropna()

    n1 = int(len(g1))
    n2 = int(len(g2))
    n = n1 + n2

    mean1 = float(g1.mean()) if n1 else None
    mean2 = float(g2.mean()) if n2 else None

    pooled = pd.concat([g1, g2], axis=0)
    mean = float(pooled.mean()) if n else None
    std = float(pooled.std(ddof=1)) if n > 1 else None

    t_stat, p_value = (np.nan, np.nan)
    if n1 >= 2 and n2 >= 2:
        # Welch (mais robusto): equal_var=False
        t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)

    return _base_contract(
        teste="t_test_two_samples",
        n=n,
        mean=mean,
        std=std,
        t_stat=None if np.isnan(t_stat) else float(t_stat),
        f_stat=None,
        p_value=None if np.isnan(p_value) else float(p_value),
        n1=n1,
        n2=n2,
        mean1=mean1,
        mean2=mean2,
        std1=float(g1.std(ddof=1)) if n1 > 1 else None,
        std2=float(g2.std(ddof=1)) if n2 > 1 else None,
    )


def teste_t_pareado(grupo1: pd.Series, grupo2: pd.Series) -> dict:
    # considera apenas pares completos
    pares = pd.concat([grupo1, grupo2], axis=1).dropna()
    g1 = pares.iloc[:, 0]
    g2 = pares.iloc[:, 1]

    n = int(len(pares))
    dif = (g1 - g2)

    mean_dif = float(dif.mean()) if n else None
    std_dif = float(dif.std(ddof=1)) if n > 1 else None

    t_stat, p_value = (np.nan, np.nan)
    if n >= 2:
        t_stat, p_value = stats.ttest_rel(g1, g2)

    mean_before = float(g1.mean()) if n else None
    mean_after = float(g2.mean()) if n else None

    return _base_contract(
        teste="t_test_paired",
        n=n,
        mean=mean_dif,  # diferença média (A − B)
        std=std_dif,
        t_stat=None if np.isnan(t_stat) else float(t_stat),
        p_value=None if np.isnan(p_value) else float(p_value),
        f_stat=None,
        mean1=mean_before,
        mean2=mean_after,
        mean_before=mean_before,
        mean_after=mean_after,
        diff_mean=mean_dif,
    )


def narrativa_t(resultado: dict, tipo: str) -> str:
    """Narrativas para Streamlit. Mostra sempre o que está sendo comparado."""
    p = resultado.get("p_value", None)
    p_txt = _fmt_p_user(p)

    if p is None or (isinstance(p, float) and np.isnan(p)):
        conclusao = "Resultado indisponível (amostra insuficiente ou dados inválidos)."
    else:
        conclusao = (
            "Há evidência estatística de diferença (p < 0,05)."
            if p < 0.05
            else "Não há evidência estatística de diferença significativa (p ≥ 0,05)."
        )

    if tipo == "1-amostra":
        mean = resultado.get("mean", None)
        mu0 = resultado.get("mu0", None)
        t_stat = resultado.get("t_stat", None)

        diff = None
        try:
            if mean is not None and mu0 is not None:
                diff = float(mean) - float(mu0)
        except Exception:
            diff = None

        obs_note = ""
        try:
            if mean is not None and mu0 is not None and abs(float(mean) - float(mu0)) < 1e-9:
                obs_note = (
                    "\n\n> Observação: μ₀ está igual à média observada; "
                    "por isso o teste tende a retornar **t ≈ 0** e **p ≈ 1**."
                )
        except Exception:
            pass

        return f"""
### Teste t — 1 amostra
Média observada: **{_fmt_num_user(mean, 2)}**  
Média hipotética (μ₀): **{_fmt_num_user(mu0, 2)}**  
Diferença (observada − μ₀): **{_fmt_num_user(diff, 2)}**  
n = {resultado.get("n")}  
t = **{_fmt_num_user(t_stat, 3)}**  
p-valor = **{p_txt}**

**Conclusão:** {conclusao}{obs_note}
"""

    if tipo == "2-amostras":
        mean1 = resultado.get("mean1", None)
        mean2 = resultado.get("mean2", None)
        n1 = resultado.get("n1", None)
        n2 = resultado.get("n2", None)
        t_stat = resultado.get("t_stat", None)

        diff = None
        try:
            if mean1 is not None and mean2 is not None:
                diff = float(mean1) - float(mean2)
        except Exception:
            diff = None

        return f"""
### Teste t — 2 amostras independentes
Grupo 1 — média: **{_fmt_num_user(mean1, 2)}** (n = {n1})  
Grupo 2 — média: **{_fmt_num_user(mean2, 2)}** (n = {n2})  
Diferença (G1 − G2): **{_fmt_num_user(diff, 2)}**  
t = **{_fmt_num_user(t_stat, 3)}**  
p-valor = **{p_txt}**

**Conclusão:** {conclusao}
"""

    if tipo == "pareado":
        t_stat = resultado.get("t_stat", None)
        diff_mean = resultado.get("mean", None)

        return f"""
### Teste t — Pareado
Diferença média (A − B): **{_fmt_num_user(diff_mean, 2)}**  
n = {resultado.get("n")}  
t = **{_fmt_num_user(t_stat, 3)}**  
p-valor = **{p_txt}**

**Conclusão:** {conclusao}
"""

    return "### Teste t\nResultado indisponível."


# ============================================================
# 2) ANOVA One-Way
# ============================================================

def anova_oneway(df: pd.DataFrame, numerica: str, categoria: str) -> dict:
    """
    ANOVA One-Way (statsmodels), robusta a:
    - espaços/BOM/caracteres estranhos no nome de coluna
    - nomes com espaço, hífen, etc.
    - evita Patsy Q() e problemas de resolução de nomes
    """
    # 1) seleciona apenas as colunas necessárias
    if numerica not in df.columns or categoria not in df.columns:
        # fallback: tenta comparar via strip (caso clássico de "Value " vs "Value")
        colmap = {c.strip(): c for c in df.columns}
        if numerica in colmap:
            numerica = colmap[numerica]
        if categoria in colmap:
            categoria = colmap[categoria]

    data = df[[numerica, categoria]].copy()

    # 2) limpeza mínima de headers (protege contra "Value ", BOM, \r)
    data.columns = [str(c).strip().replace("\ufeff", "") for c in data.columns]
    numerica_clean, categoria_clean = data.columns[0], data.columns[1]

    # 3) dropna e rename temporário (contrato robusto para Patsy)
    data = data.dropna()
    n = int(len(data))

    mean = float(data[numerica_clean].mean()) if n else None
    std = float(data[numerica_clean].std(ddof=1)) if n > 1 else None

    tmp = data.rename(columns={numerica_clean: "__y__", categoria_clean: "__g__"})

    # regra: precisa ter ao menos 2 grupos
    if tmp["__g__"].nunique(dropna=True) < 2:
        raise ValueError("ANOVA One-Way exige pelo menos 2 grupos na variável categórica.")

    modelo = smf.ols("__y__ ~ C(__g__)", data=tmp).fit()
    tabela = sm.stats.anova_lm(modelo, typ=2)

    f_stat = float(tabela["F"].iloc[0])
    p_value = float(tabela["PR(>F)"].iloc[0])

    return _base_contract(
        teste="anova_oneway",
        n=n,
        mean=mean,
        std=std,
        t_stat=None,
        f_stat=f_stat,
        p_value=p_value,
        value_column=str(numerica),   # mantém o nome original selecionado
        group_column=str(categoria),
        anova_table=tabela,
    )



def narrativa_anova(resultado: dict) -> str:
    p = resultado.get("p_value", None)
    f = resultado.get("f_stat", None)

    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "### ANOVA One-Way\nResultado indisponível."

    conclusao = (
        "Há diferença significativa entre pelo menos dois grupos (p < 0,05)."
        if p < 0.05
        else "Não há evidência de diferença significativa entre os grupos (p ≥ 0,05)."
    )

    return f"""
### ANOVA One-Way
F = **{_fmt_num_user(f, 3)}**  
p-valor = **{_fmt_p_user(p)}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 3) Qui-quadrado
# ============================================================

def teste_quiquadrado(df: pd.DataFrame, cat1: str, cat2: str) -> dict:
    tabela = pd.crosstab(df[cat1], df[cat2])
    chi2, p, dof, expected = stats.chi2_contingency(tabela)

    n = int(tabela.values.sum())

    return _base_contract(
        teste="chi_square",
        n=n,
        mean=None,
        std=None,
        t_stat=None,
        f_stat=float(chi2),  # aqui usamos f_stat como "stat" geral (χ²)
        p_value=float(p),
        cat1=str(cat1),
        cat2=str(cat2),
        dof=int(dof),
        table=tabela,
        expected=expected,
    )


def narrativa_quiquadrado(resultado: dict) -> str:
    p = resultado.get("p_value", None)
    chi2 = resultado.get("f_stat", None)
    dof = resultado.get("dof", None)

    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "### Teste Qui-Quadrado\nResultado indisponível."

    conclusao = (
        "Há associação estatística entre as variáveis (p < 0,05)."
        if p < 0.05
        else "Não há evidência de associação estatística (p ≥ 0,05)."
    )

    return f"""
### Teste Qui-Quadrado
χ² = **{_fmt_num_user(chi2, 3)}** (gl = {dof})  
p-valor = **{_fmt_p_user(p)}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 4) Normalidade + QQPlot
# ============================================================

def teste_normalidade(serie: pd.Series, metodo: str = "shapiro") -> dict:
    serie = serie.dropna()
    n = int(len(serie))

    mean = float(serie.mean()) if n else None
    std = float(serie.std(ddof=1)) if n > 1 else None

    if n < 3:
        return _base_contract(
            teste=f"normality_{metodo}",
            n=n,
            mean=mean,
            std=std,
            t_stat=None,
            f_stat=None,
            p_value=None,
            metodo=str(metodo),
            w_stat=None,
        )

    stat, p = stats.shapiro(serie)

    return _base_contract(
        teste=f"normality_{metodo}",
        n=n,
        mean=mean,
        std=std,
        t_stat=float(stat),
        f_stat=None,
        p_value=float(p),
        metodo=str(metodo),
        w_stat=float(stat),
    )


def qqplot_figure(serie: pd.Series) -> go.Figure:
    """QQ-Plot em Plotly para visualização em Streamlit."""
    serie = serie.dropna()
    (osm, osr), (slope, intercept, r) = stats.probplot(serie, dist="norm")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=osm,
            y=osr,
            mode="markers",
            name="Amostra",
            marker=dict(color=PRIMARY),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=osm,
            y=slope * osm + intercept,
            mode="lines",
            name="Linha de Referência",
            line=dict(color=SECONDARY, width=2),
        )
    )
    fig.update_layout(
        title="QQ-Plot (Normal)",
        xaxis_title="Quantis Teóricos",
        yaxis_title="Quantis Observados",
        template="plotly_white",
    )
    return fig


def narrativa_normalidade(resultado: dict) -> str:
    p = resultado.get("p_value", None)
    metodo = resultado.get("metodo", resultado.get("teste", "shapiro"))

    if p is None or (isinstance(p, float) and np.isnan(p)):
        return f"O teste de normalidade ({metodo}) não pôde ser calculado por falta de dados."

    conclusao = (
        "Os dados **não seguem** distribuição normal (p < 0,05)."
        if p < 0.05
        else "Os dados **seguem** distribuição aproximadamente normal (p ≥ 0,05)."
    )

    return f"""
### Teste de Normalidade — {metodo}
p-valor = **{_fmt_p_user(p)}**

**Conclusão:** {conclusao}
"""
