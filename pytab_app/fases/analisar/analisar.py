import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pytab.charts.theme import apply_pytab_theme, PRIMARY, SECONDARY
apply_pytab_theme()

from pytab_app.modules.testes_estatisticos import (
    teste_t_uma_amostra, teste_t_duas_amostras, teste_t_pareado, narrativa_t,
    anova_oneway, narrativa_anova,
    teste_quiquadrado, narrativa_quiquadrado,
    teste_normalidade, qqplot_figure, narrativa_normalidade
)

# ==================================================================
#  ABA 1 – CORRELAÇÃO
# ==================================================================

def aba_correlacao(df):
    st.subheader("Correlação entre Variáveis Numéricas")

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(num_cols) < 2:
        st.info("É necessário pelo menos duas variáveis numéricas.")
        return

    corr = df[num_cols].corr()

    # Heatmap
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
    ax.set_title("Matriz de Correlação", fontsize=12)
    st.pyplot(fig)
    plt.close(fig)

    # Narrativa automática
    maior = corr.replace(1, np.nan).abs().max().max()
    var = corr.abs().stack().sort_values(ascending=False).index[0]

    st.markdown(f"""
### Narrativa automática
A maior correlação encontrada foi **{maior:.2f}** entre **{var[0]}** e **{var[1]}**.  
Isso indica uma relação linear relevante entre essas variáveis.
""")

# ==================================================================
#  ABA 2 – PARETO
# ==================================================================

def aba_pareto(df):
    st.subheader("Análise de Pareto")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        st.info("Nenhuma coluna categórica encontrada.")
        return

    coluna = st.selectbox("Selecione a categoria", cat_cols)

    dados = df[coluna].value_counts().sort_values(ascending=False)
    total = dados.sum()
    percentual = dados.cumsum() / total * 100

    # Gráfico Pareto (Plotly)
    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_bar(
        x=dados.index,
        y=dados.values,
        marker_color=PRIMARY,
        name="Frequência"
    )

    fig.add_trace(
        go.Scatter(
            x=dados.index,
            y=percentual,
            mode="lines+markers",
            line=dict(color=SECONDARY, width=3),
            name="Cumulativo (%)",
            yaxis="y2"
        )
    )

    fig.update_layout(
        title="Gráfico de Pareto",
        yaxis=dict(title="Frequência"),
        yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 100]),
        xaxis=dict(title=coluna),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Narrativa automática
    top = dados.index[0]
    top_pct = dados.iloc[0] / total * 100

    st.markdown(f"""
### Narrativa automática
O item mais frequente é **{top}**, representando **{top_pct:.1f}%** das ocorrências totais.  
Isso reforça o princípio do Pareto: poucos itens concentram grande parte do impacto.
""")

# ==================================================================
#  ABA 3 – REGRESSÃO
# ==================================================================

def aba_regressao(df):
    st.subheader("Regressão Linear Simples")

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(num_cols) < 2:
        st.info("É necessário pelo menos duas variáveis numéricas.")
        return

    col1 = st.selectbox("Variável Dependente (Y)", num_cols)
    col2 = st.selectbox("Variável Independente (X)", num_cols)

    if col1 == col2:
        st.warning("Escolha variáveis diferentes.")
        return

    # Regressão
    import statsmodels.api as sm
    X = sm.add_constant(df[col2])
    modelo = sm.OLS(df[col1], X).fit()

    st.write(modelo.summary())

    # Gráfico regressão
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(df[col2], df[col1], color=PRIMARY, alpha=0.6)

    linha = modelo.params["const"] + modelo.params[col2] * df[col2]
    ax.plot(df[col2], linha, color=SECONDARY, linewidth=2)

    ax.set_title("Regressão Linear Simples")
    ax.set_xlabel(col2)
    ax.set_ylabel(col1)

    st.pyplot(fig)
    plt.close(fig)

    # Narrativa
    coef = modelo.params[col2]
    p = modelo.pvalues[col2]

    st.markdown(f"""
### Narrativa automática
A regressão indica que:

- Cada aumento de **1 unidade** em **{col2}** altera **{col1}** em **{coef:.3f}** unidades.
- p-valor = **{p:.4f}**

**Conclusão:** {"Há evidência de relação linear." if p < 0.05 else "Não há evidência de relação linear significativa."}
""")

# ==================================================================
#  ABA 4 – TESTES ESTATÍSTICOS
# ==================================================================

def aba_testes(df):

    st.subheader("Testes Estatísticos")

    cols = df.columns.tolist()

    tipo = st.selectbox(
        "Selecione o tipo de teste",
        [
            "Teste t — 1 amostra",
            "Teste t — 2 amostras",
            "Teste t — Pareado",
            "ANOVA One-Way",
            "Qui-Quadrado",
            "Normalidade"
        ]
    )

    # ---------------------- TESTE t 1 AMOSTRA ----------------------
    if tipo == "Teste t — 1 amostra":
        col = st.selectbox("Selecione a variável numérica", df.select_dtypes(include=["number"]).columns)
        media_hip = st.number_input("Média hipotética", value=0.0)
        res = teste_t_uma_amostra(df[col], media_hip)
        st.markdown(narrativa_t(res, "1-amostra"))

    # ---------------------- TESTE t 2 AMOSTRAS ----------------------
    elif tipo == "Teste t — 2 amostras":
        numcol = st.selectbox("Selecione variável numérica", df.select_dtypes(include=["number"]).columns)
        cat = st.selectbox("Selecione variável categórica", df.select_dtypes(include=["object", "category"]).columns)

        grupos = df[cat].dropna().unique()
        if len(grupos) != 2:
            st.warning("Selecione uma variável categórica com exatamente 2 grupos.")
            return

        g1 = df[df[cat] == grupos[0]][numcol]
        g2 = df[df[cat] == grupos[1]][numcol]

        res = teste_t_duas_amostras(g1, g2)
        st.markdown(narrativa_t(res, "2-amostras"))

    # ---------------------- PAREADO ----------------------
    elif tipo == "Teste t — Pareado":
        cols_num = df.select_dtypes(include=["number"]).columns
        col1 = st.selectbox("Primeira variável", cols_num)
        col2 = st.selectbox("Segunda variável", cols_num)
        res = teste_t_pareado(df[col1], df[col2])
        st.markdown(narrativa_t(res, "pareado"))

    # ---------------------- ANOVA ----------------------
    elif tipo == "ANOVA One-Way":
        numcol = st.selectbox("Variável numérica", df.select_dtypes(include=["number"]).columns)
        cat = st.selectbox("Variável categórica", df.select_dtypes(include=["object", "category"]).columns)
        res = anova_oneway(df, numcol, cat)
        st.write(res["anova"])
        st.markdown(narrativa_anova(res))

    # ---------------------- QUI QUADRADO ----------------------
    elif tipo == "Qui-Quadrado":
        c1 = st.selectbox("Variável categórica 1", df.select_dtypes(include=["object", "category"]).columns)
        c2 = st.selectbox("Variável categórica 2", df.select_dtypes(include=["object", "category"]).columns)
        res = teste_quiquadrado(df, c1, c2)
        st.write(res["tabela"])
        st.markdown(narrativa_quiquadrado(res))

    # ---------------------- NORMALIDADE ----------------------
    elif tipo == "Normalidade":
        col = st.selectbox("Variável numérica", df.select_dtypes(include=["number"]).columns)
        res = teste_normalidade(df[col])
        st.markdown(narrativa_normalidade(res))
        fig = qqplot_figure(df[col])
        st.plotly_chart(fig, use_container_width=True)


# ==================================================================
#  FUNÇÃO PRINCIPAL DA FASE ANALISAR
# ==================================================================

def fase_analisar(df):
    st.header("Fase Analisar — Identificação de Causas e Padrões")

    aba = st.tabs(["Correlação", "Pareto", "Regressão", "Testes Estatísticos"])

    with aba[0]:
        aba_correlacao(df)

    with aba[1]:
        aba_pareto(df)

    with aba[2]:
        aba_regressao(df)

    with aba[3]:
        aba_testes(df)
