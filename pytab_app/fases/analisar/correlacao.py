import pandas as pd
import streamlit as st
import plotly.express as px

from pytab.charts.theme import style_plotly
from .narrativas import gerar_narrativa_correlacao


def analisar_correlacao(df: pd.DataFrame) -> dict | None:
    """
    Renderiza a seção de correlação e retorna um resumo para narrativas.
    """

    st.subheader("Correlação entre variáveis")

    numeric_cols = df.select_dtypes(include=["number", "float", "int"]).columns.tolist()
    if len(numeric_cols) < 2:
        st.info("É necessário ter pelo menos duas colunas numéricas para análise de correlação.")
        return None

    cols = st.multiselect(
        "Selecione as variáveis numéricas para incluir na matriz de correlação",
        options=numeric_cols,
        default=numeric_cols[: min(4, len(numeric_cols))],
    )

    if len(cols) < 2:
        st.info("Selecione pelo menos duas variáveis para calcular a correlação.")
        return None

    data = df[cols].dropna()
    if data.empty:
        st.warning("Não há dados suficientes após remover valores ausentes.")
        return None

    corr = data.corr()

    # Heatmap
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title="Matriz de correlação",
    )
    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    # Lista das principais correlações (pares)
    pares = []
    n = len(corr.columns)
    cols_corr = corr.columns.tolist()
    for i in range(n):
        for j in range(i + 1, n):
            r = corr.iloc[i, j]
            pares.append(
                {
                    "Var1": cols_corr[i],
                    "Var2": cols_corr[j],
                    "Correlação": r,
                    "Abs": abs(r),
                }
            )

    if not pares:
        st.info("Não foi possível calcular pares de correlação.")
        return None

    df_pares = pd.DataFrame(pares).sort_values("Abs", ascending=False)
    st.markdown("Principais relações (em ordem de força absoluta):")
    st.dataframe(df_pares[["Var1", "Var2", "Correlação"]].head(5), use_container_width=True)

    melhor = df_pares.iloc[0]
    summary = {
        "var1": melhor["Var1"],
        "var2": melhor["Var2"],
        "corr": float(melhor["Correlação"]),
    }

    texto = gerar_narrativa_correlacao(summary)
    st.markdown(texto)

    return summary
