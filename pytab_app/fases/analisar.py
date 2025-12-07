import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pytab.theme import apply_pytab_theme

apply_pytab_theme()

PRIMARY = "#1f77b4"
SECONDARY = "#ec7f00"



def fase_analisar(df: pd.DataFrame):
    st.header("Fase Analisar — Identificação de Padrões e Outliers")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.warning("Nenhuma coluna numérica disponível para análise.")
        return

    indicador = st.selectbox("Selecione o indicador", numeric_cols)

    z_lim = st.slider("Z-Score para detectar outliers", 1.5, 4.0, 3.0, step=0.1)

    serie = df[indicador].dropna()
    media = serie.mean()
    desvio = serie.std()

    z_scores = (serie - media) / desvio
    outliers = serie[abs(z_scores) > z_lim]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Média", f"{media:,.2f}")
    with col2:
        st.metric("Desvio Padrão", f"{desvio:,.2f}")

    st.write(f"Foram encontrados **{len(outliers)} outliers** usando Z > {z_lim}")

    # Gráfico de densidade com outliers marcados
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(serie.index, serie.values, color=PRIMARY, alpha=0.6, label="Valores")
    ax.scatter(outliers.index, outliers.values, color=SECONDARY, label="Outliers", s=60)
    ax.axhline(media, color="#444444", linestyle="--", linewidth=1, label="Média")

    ax.set_title(f"Distribuição e Outliers — {indicador}")
    ax.set_ylabel(indicador)
    ax.grid(True, alpha=0.25)
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)

    # Pareto de magnitude dos desvios
    desvios_abs = (serie - media).abs().sort_values(ascending=False)

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.bar(desvios_abs.index[:15], desvios_abs.values[:15], color=PRIMARY)
    ax2.set_title(f"Pareto — 15 maiores desvios absolutos ({indicador})")
    ax2.set_ylabel("Desvio absoluto")
    ax2.grid(True, alpha=0.25)

    st.pyplot(fig2)
    plt.close(fig2)
