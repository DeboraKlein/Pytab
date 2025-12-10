import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import plotly.graph_objects as go

from pytab.charts.theme import PRIMARY, SECONDARY


# ============================================================
# 1) TESTES t
# ============================================================

def teste_t_uma_amostra(serie, media_hipotetica):
    serie = serie.dropna()
    t_stat, p = stats.ttest_1samp(serie, media_hipotetica)

    return {
        "media": serie.mean(),
        "t": float(t_stat),
        "p": float(p),
        "hipotese": media_hipotetica
    }


def teste_t_duas_amostras(grupo1, grupo2):
    grupo1 = grupo1.dropna()
    grupo2 = grupo2.dropna()

    t_stat, p = stats.ttest_ind(grupo1, grupo2, equal_var=False)

    return {
        "media1": grupo1.mean(),
        "media2": grupo2.mean(),
        "t": float(t_stat),
        "p": float(p),
    }


def teste_t_pareado(grupo1, grupo2):
    grupo1 = grupo1.dropna()
    grupo2 = grupo2.dropna()

    t_stat, p = stats.ttest_rel(grupo1, grupo2)

    return {
        "media1": grupo1.mean(),
        "media2": grupo2.mean(),
        "t": float(t_stat),
        "p": float(p),
    }


def narrativa_t(resultado, tipo):
    p = resultado["p"]
    conclusao = "Há evidência estatística de diferença." if p < 0.05 else "Não há evidência de diferença significativa."

    if tipo == "1-amostra":
        return f"""
### Teste t — 1 amostra
Média observada: **{resultado['media']:.2f}**  
Média hipotética: **{resultado['hipotese']}**  
p-valor: **{p:.4f}**

**Conclusão:** {conclusao}
"""

    else:
        return f"""
### Teste t — {tipo}
Média do grupo 1: **{resultado['media1']:.2f}**  
Média do grupo 2: **{resultado['media2']:.2f}**  
p-valor: **{p:.4f}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 2) ANOVA
# ============================================================

def anova_oneway(df, numerica, categoria):
    df = df[[numerica, categoria]].dropna()

    modelo = smf.ols(f"{numerica} ~ C({categoria})", data=df).fit()
    tabela = sm.stats.anova_lm(modelo)

    return {
        "anova": tabela,
        "modelo": modelo
    }


def narrativa_anova(resultado):
    tabela = resultado["anova"]
    p = tabela["PR(>F)"][0]

    conclusao = "Há diferença estatística entre os grupos." if p < 0.05 else "Não há evidência de diferença estatística."

    return f"""
### ANOVA One-Way
p-valor: **{p:.4f}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 3) QUI-QUADRADO
# ============================================================

def teste_quiquadrado(df, cat1, cat2):
    tabela = pd.crosstab(df[cat1], df[cat2])
    chi2, p, gl, esperado = stats.chi2_contingency(tabela)

    return {
        "tabela": tabela,
        "chi2": float(chi2),
        "p": float(p),
        "gl": int(gl)
    }


def narrativa_quiquadrado(resultado):
    p = resultado["p"]
    conclusao = (
        "Existe associação entre as variáveis."
        if p < 0.05
        else "Não há evidência de associação entre as variáveis."
    )

    return f"""
### Teste Qui-Quadrado
Chi² = **{resultado['chi2']:.2f}**  
p-valor = **{resultado['p']:.4f}**

**Conclusão:** {conclusao}
"""


# ============================================================
# 4) NORMALIDADE
# ============================================================

def teste_normalidade(series):
    series = series.dropna()

    try:
        stat, p = stats.shapiro(series)
        metodo = "Shapiro-Wilk"
    except:
        stat, p = stats.anderson(series)[0], None
        metodo = "Anderson-Darling"

    return {
        "metodo": metodo,
        "stat": float(stat),
        "p": None if p is None else float(p)
    }


def qqplot_figure(series):
    series = series.dropna()
    fig = go.Figure()

    qq = sm.ProbPlot(series, fit=True)
    linha = qq.theoretical_quantiles
    pontos = qq.sample_quantiles

    fig.add_trace(go.Scatter(x=linha, y=pontos, mode="markers", marker=dict(color=PRIMARY)))
    fig.add_trace(go.Scatter(x=linha, y=linha, mode="lines", line=dict(color=SECONDARY)))

    fig.update_layout(title="QQ-Plot", xaxis_title="Quantis Teóricos", yaxis_title="Quantis Observados")
    return fig


def narrativa_normalidade(resultado):
    metodo = resultado["metodo"]
    p = resultado["p"]

    if p is None:
        return f"O teste {metodo} foi aplicado. Use a análise visual do QQ-Plot para interpretar."

    conclusao = (
        "Os dados **não seguem** distribuição normal." if p < 0.05 else "Os dados **seguem** distribuição normal."
    )

    return f"""
### Teste de Normalidade — {metodo}
p-valor = **{p:.4f}**

**Conclusão:** {conclusao}
"""


# ============================================================
# FIM DO MÓDULO
# ============================================================
