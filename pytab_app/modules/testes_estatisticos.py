"""
pytab_app.modules.testes_estatisticos

Contrato estatístico (base) para validação automática:

    {
      "teste": str,
      "n": int,
      "mean": float | None,
      "std": float | None,
      "t_stat": float | None,
      "f_stat": float | None,
      "p_value": float | None,
    }

Observação:
- Funções podem retornar campos adicionais (ex.: mu0, n1, n2, mean1, mean2, dof, table),
  mas DEVEM sempre incluir o contrato base acima para o validate_suite.
"""

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
# Helpers
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
    if n >= 2 and std is not None and np.isfinite(std) and std != 0:
        t_stat, p_value = stats.ttest_1samp(serie, popmean=float(mu0))

    return _base_contract(
        teste="t_test_one_sample",
        n=n,
        mean=mean,
        std=std,
        t_stat=None if np.isnan(t_stat) else float(t_stat),
        p_value=None if np.isnan(p_value) else float(p_value),
        f_stat=None,
        mu0=float(mu0),
    )


def teste_t_duas_amostras(
    grupo1: pd.Series,
    grupo2: pd.Series,
    equal_var: bool = False,
) -> dict:
    g1 = grupo1.dropna()
    g2 = grupo2.dropna()

    n1 = int(len(g1))
    n2 = int(len(g2))
    n = n1 + n2

    mean1 = float(g1.mean()) if n1 else None
    mean2 = float(g2.mean()) if n2 else None

    pooled = pd.concat([g1, g2], axis=0)
    std = float(pooled.std(ddof=1)) if n > 1 else None
    mean = float(pooled.mean()) if n else None

    t_stat, p_value = (np.nan, np.nan)
    if n1 >= 2 and n2 >= 2:
        t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=bool(equal_var))

    return _base_contract(
        teste="t_test_two_samples",
        n=n,
        mean=mean,
        std=std,
        t_stat=None if np.isnan(t_stat) else float(t_stat),
        p_value=None if np.isnan(p_value) else float(p_value),
        f_stat=None,
        n1=n1,
        n2=n2,
        mean1=mean1,
        mean2=mean2,
        equal_var=bool(equal_var),
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

    return _base_contract(
        teste="t_test_paired",
        n=n,
        mean=mean_dif,     # diferença média (A − B)
        std=std_dif,
        t_stat=None if np.isnan(t_stat) else float(t_stat),
        p_value=None if np.isnan(p_value) else float(p_value),
        f_stat=None,
        mean1=float(g1.mean()) if n else None,
        mean2=float(g2.mean()) if n else None,
    )


def narrativa_t(resultado: dict, tipo: str) -> str:
    """Narrativas para Streamlit. Usa o contrato base + extras quando disponíveis."""
    p = resultado.get("p_value", None)

    conclusao = (
        "Há evidência estatística de diferença (p < 0,05)."
        if (p is not None and p < 0.05)
        else "Não há evidência estatística de diferença significativa (p ≥ 0,05)."
    )

    if tipo == "1-amostra":
        return f"""
### Teste t — 1 amostra
Média observada: **{resultado.get('mean', float('nan')):.2f}**  
Média hipotética: **{resultado.get('mu0', float('nan')):.2f}**  
n = {resultado.get('n')}  
t = {resultado.get('t_stat', float('nan')):.3f}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

    if tipo == "2-amostras":
        return f"""
### Teste t — 2 amostras independentes
Grupo 1 — média: **{resultado.get('mean1', float('nan')):.2f}** (n = {resultado.get('n1')})  
Grupo 2 — média: **{resultado.get('mean2', float('nan')):.2f}** (n = {resultado.get('n2')})  
t = {resultado.get('t_stat', float('nan')):.3f}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

    if tipo == "pareado":
        return f"""
### Teste t — Pareado
Diferença média (A − B): **{resultado.get('mean', float('nan')):.2f}**  
n = {resultado.get('n')}  
t = {resultado.get('t_stat', float('nan')):.3f}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

    return """### Teste t\nResultado indisponível."""


# ============================================================
# 2) ANOVA One-Way
# ============================================================

def anova_oneway(df: pd.DataFrame, numerica: str, categoria: str) -> dict:
    """ANOVA One-Way (statsmodels). Usa Q() para colunas com espaços/caracteres especiais."""
    data = df[[numerica, categoria]].dropna()
    n = int(len(data))

    mean = float(data[numerica].mean()) if n else None
    std = float(data[numerica].std(ddof=1)) if n > 1 else None

    # Formula segura (patsy Q)
    # Ex.: Q("Unit Value") ~ C(Q("Team"))
    formula = f'{Q(numerica)} ~ C({Q(categoria)})'

    modelo = smf.ols(formula, data=data).fit()
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
        value_column=str(numerica),
        group_column=str(categoria),
        anova_table=tabela,
    )


def narrativa_anova(resultado: dict) -> str:
    p = resultado.get("p_value", None)
    f = resultado.get("f_stat", None)

    conclusao = (
        "Há diferença significativa entre pelo menos dois grupos (p < 0,05)."
        if (p is not None and p < 0.05)
        else "Não há evidência de diferença significativa entre os grupos (p ≥ 0,05)."
    )

    return f"""
### ANOVA One-Way
F = **{f:.3f}**  
p-valor = **{p:.4f}**

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
        f_stat=float(chi2),  # usamos f_stat como "stat" geral (chi²) no contrato
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

    conclusao = (
        "Há associação estatística entre as variáveis (p < 0,05)."
        if (p is not None and p < 0.05)
        else "Não há evidência de associação estatística (p ≥ 0,05)."
    )

    return f"""
### Teste Qui-Quadrado
χ² = **{chi2:.3f}** (gl = {dof})  
p-valor = **{p:.4f}**

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
        )

    # Por enquanto: Shapiro como padrão (robusto e popular no LSS)
    stat, p = stats.shapiro(serie)

    return _base_contract(
        teste=f"normality_{metodo}",
        n=n,
        mean=mean,
        std=std,
        t_stat=float(stat),   # usamos t_stat como "stat" geral
        f_stat=None,
        p_value=float(p),
        metodo=str(metodo),
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

    conclusao = (
        "Os dados **não seguem** distribuição normal (p < 0,05)."
        if (p is not None and p < 0.05)
        else "Os dados **seguem** distribuição aproximadamente normal (p ≥ 0,05)."
    )

    return f"""
### Teste de Normalidade — {metodo}
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""
