import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import plotly.graph_objects as go

from pytab.charts.theme import PRIMARY, SECONDARY


# ============================================================
# 1) TESTES t
# ============================================================


def teste_t_uma_amostra(serie: pd.Series, mu0: float) -> dict:
    serie = serie.dropna()
    n = int(len(serie))

    mean = float(serie.mean())
    std = float(serie.std(ddof=1))

    t_stat, p_value = stats.ttest_1samp(serie, popmean=mu0)

    return {
        "teste": "t_test_one_sample",
        "n": n,
        "mean": mean,
        "std": std,
        "t_stat": float(t_stat),
        "f_stat": None,
        "p_value": float(p_value),
    }



def teste_t_duas_amostras(
    grupo1: pd.Series,
    grupo2: pd.Series,
    equal_var: bool = False,
) -> dict:
    g1 = grupo1.dropna()
    g2 = grupo2.dropna()

    t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=equal_var)

    return {
        "teste": "t_test_two_samples",
        "n": int(len(g1) + len(g2)),
        "mean": float((g1.mean() + g2.mean()) / 2),
        "std": float(pd.concat([g1, g2]).std(ddof=1)),
        "t_stat": float(t_stat),
        "f_stat": None,
        "p_value": float(p_value),
    }



def teste_t_pareado(grupo1: pd.Series, grupo2: pd.Series) -> dict:
    # considera apenas pares completos
    df = pd.concat([grupo1, grupo2], axis=1).dropna()
    g1 = df.iloc[:, 0]
    g2 = df.iloc[:, 1]

    t_stat, p = stats.ttest_rel(g1, g2)

    return {
        "media1": float(g1.mean()),
        "media2": float(g2.mean()),
        "n": int(df.shape[0]),
        "t": float(t_stat),
        "p": float(p),
    }


def narrativa_t(resultado: dict, tipo: str) -> str:
    p = resultado["p"]
    conclusao = (
        "Há evidência estatística de diferença."
        if p < 0.05
        else "Não há evidência estatística de diferença significativa."
    )

    if tipo == "1-amostra":
        return f"""
### Teste t — 1 amostra
Média observada: **{resultado['media']:.2f}**  
Média hipotética: **{resultado['hipotese']}**  
n = {resultado['n']}  
t = {resultado['t']:.3f}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

    if tipo == "2-amostras":
        return f"""
### Teste t — 2 amostras independentes
Grupo 1 — média: **{resultado['media1']:.2f}** (n = {resultado['n1']})  
Grupo 2 — média: **{resultado['media2']:.2f}** (n = {resultado['n2']})  
t = {resultado['t']:.3f}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

    if tipo == "pareado":
        return f"""
### Teste t — pareado
Média antes: **{resultado['media1']:.2f}**  
Média depois: **{resultado['media2']:.2f}**  
n pares = {resultado['n']}  
t = {resultado['t']:.3f}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

    return f"Teste t ({tipo}) executado. p-valor = {p:.4f}. {conclusao}"


# ============================================================
# 2) ANOVA ONE-WAY
# ============================================================

def anova_oneway(df: pd.DataFrame, numerica: str, categoria: str) -> dict:
    """
    ANOVA One-Way
    H0: médias dos grupos são iguais
    """

    data = df[[numerica, categoria]].dropna()
    n = int(len(data))

    modelo = smf.ols(f"{numerica} ~ C({categoria})", data=data).fit()
    tabela = sm.stats.anova_lm(modelo, typ=2)

    f_stat = float(tabela["F"].iloc[0])
    p_value = float(tabela["PR(>F)"].iloc[0])

    return {
        "teste": "anova_oneway",
        "n": n,
        "mean": float(data[numerica].mean()),
        "std": float(data[numerica].std(ddof=1)),
        "t_stat": None,
        "f_stat": f_stat,
        "p_value": p_value,
    }

def narrativa_anova(resultado: dict) -> str:
    tabela = resultado["anova"]
    p = float(tabela["PR(>F)"].iloc[0])

    conclusao = (
        "Há diferença estatística entre pelo menos um dos grupos."
        if p < 0.05
        else "Não há evidência estatística de diferença entre as médias dos grupos."
    )

    return f"""
### ANOVA One-Way
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 3) QUI-QUADRADO
# ============================================================

def teste_quiquadrado(df: pd.DataFrame, cat1: str, cat2: str) -> dict:
    tabela = pd.crosstab(df[cat1], df[cat2])
    chi2, p, dof, expected = stats.chi2_contingency(tabela)

    return {
        "tabela": tabela,
        "chi2": float(chi2),
        "p": float(p),
        "dof": int(dof),
        "esperado": expected,
    }


def narrativa_quiquadrado(resultado: dict) -> str:
    p = resultado["p"]
    conclusao = (
        "Há evidência de associação entre as variáveis."
        if p < 0.05
        else "Não há evidência estatística de associação entre as variáveis."
    )

    return f"""
### Teste Qui-Quadrado
Qui² = {resultado['chi2']:.3f}  
gl = {resultado['dof']}  
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 4) NORMALIDADE + QQ-PLOT
# ============================================================

def teste_normalidade(serie: pd.Series, metodo: str = "shapiro") -> dict:
    serie = serie.dropna()

    if serie.shape[0] < 3:
        return {"metodo": metodo, "p": None, "stat": None}

    if metodo == "shapiro":
        stat, p = stats.shapiro(serie)
    else:
        # por enquanto mantemos apenas Shapiro como padrão
        stat, p = stats.shapiro(serie)

    return {
        "metodo": metodo,
        "stat": float(stat),
        "p": float(p),
    }


def qqplot_figure(serie: pd.Series) -> go.Figure:
    serie = serie.dropna()
    qq = sm.ProbPlot(serie, fit=True)

    teoricos = qq.theoretical_quantiles
    amostra = qq.sample_quantiles

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=teoricos,
            y=amostra,
            mode="markers",
            marker=dict(color=PRIMARY, size=6),
            name="Dados",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=teoricos,
            y=teoricos,
            mode="lines",
            line=dict(color=SECONDARY, width=2),
            name="Linha Normal",
        )
    )

    fig.update_layout(
        title="QQ-Plot",
        xaxis_title="Quantis teóricos",
        yaxis_title="Quantis observados",
    )

    return fig


def narrativa_normalidade(resultado: dict) -> str:
    metodo = resultado["metodo"]
    p = resultado["p"]

    if p is None:
        return f"O teste de normalidade ({metodo}) não pôde ser calculado por falta de dados."

    conclusao = (
        "Os dados **não seguem** distribuição normal (p < 0,05)."
        if p < 0.05
        else "Os dados **seguem** distribuição aproximadamente normal (p ≥ 0,05)."
    )

    return f"""
### Teste de Normalidade — {metodo}
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""

