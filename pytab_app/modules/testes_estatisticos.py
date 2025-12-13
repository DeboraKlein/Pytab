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


def teste_t_uma_amostra(serie, mu0: float):
    """
    Teste t de uma amostra.
    H0: média = mu0
    """

    serie = serie.dropna()
    n = len(serie)

    mean = float(np.mean(serie))
    std = float(np.std(serie, ddof=1))  # desvio padrão amostral

    t_stat, p_value = stats.ttest_1samp(serie, popmean=mu0)

    return {
        "teste": "t_test_one_sample",
        "n": n,
        "mu0": float(mu0),
        "mean": mean,
        "std": std,
        "t_stat": float(t_stat),
        "p_value": float(p_value),
    }



def teste_t_duas_amostras(
    grupo1: pd.Series,
    grupo2: pd.Series,
    equal_var: bool = False,
) -> dict:
    grupo1 = grupo1.dropna()
    grupo2 = grupo2.dropna()

    t_stat, p = stats.ttest_ind(grupo1, grupo2, equal_var=equal_var)
    return {
        "media1": float(grupo1.mean()),
        "media2": float(grupo2.mean()),
        "n1": int(grupo1.shape[0]),
        "n2": int(grupo2.shape[0]),
        "t": float(t_stat),
        "p": float(p),
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
    Executa ANOVA One-Way lidando com nomes de coluna com espaço.

    Renomeia colunas para nomes seguros internamente e usa statsmodels.
    """
    dados = df[[numerica, categoria]].dropna()

    if dados.empty:
        raise ValueError("Não há dados suficientes para ANOVA.")

    y_name = "y_var"
    x_name = "x_cat"
    dados_local = dados.rename(columns={numerica: y_name, categoria: x_name})

    modelo = smf.ols(f"{y_name} ~ C({x_name})", data=dados_local).fit()
    tabela = sm.stats.anova_lm(modelo, typ=2)

    return {"anova": tabela, "modelo": modelo, "y": numerica, "x": categoria}


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

