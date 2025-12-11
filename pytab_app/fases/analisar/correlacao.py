import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pytab.charts.theme import apply_pytab_theme

apply_pytab_theme()

PRIMARY = "#1f77b4"
SECONDARY = "#ec7f00"


def calcular_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna:
      - matriz de correlação (pandas.DataFrame)
      - par de maior correlação entre variáveis distintas
      - valor da correlação
    """
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if len(num_cols) < 2:
        return None, None, None

    corr = df[num_cols].corr()

    corr_abs = corr.abs().copy()
    # Remove diagonal (correlação da variável com ela mesma)
    np.fill_diagonal(corr_abs.values, np.nan)

    # Caso especial: nenhuma correlação válida
    if corr_abs.isna().all().all():
        return corr, None, None

    # Encontrar maior correlação |valor|
    idx_max = corr_abs.unstack().idxmax()
    var1, var2 = idx_max
    maior = corr.loc[var1, var2]

    return corr, (var1, var2), maior


def classificar_correlacao(valor: float) -> str:
    """
    Retorna uma classificação textual da correlação.
    """
    if valor is None:
        return "sem correlação relevante"

    v = abs(valor)
    if v < 0.2:
        return "muito fraca"
    elif v < 0.4:
        return "fraca"
    elif v < 0.6:
        return "moderada"
    elif v < 0.8:
        return "forte"
    else:
        return "muito forte"


def direcao(valor: float) -> str:
    if valor > 0:
        return "positiva"
    else:
        return "negativa"


def mostrar_correlacao_streamlit(df: pd.DataFrame):
    """
    Renderiza toda a aba de correlação no Streamlit.
    """
    st.subheader("Correlação entre Variáveis Numéricas")

    corr, par, valor = calcular_correlacao(df)

    if corr is None:
        st.info("É necessário pelo menos duas variáveis numéricas.")
        return

    # ----- Heatmap -----
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
    ax.set_title("Matriz de Correlação", fontsize=12)
    st.pyplot(fig)
    plt.close(fig)

    # ----- Narrativa -----
    st.markdown("### Narrativa automática")

    if par is None:
        st.markdown("Não foram identificadas correlações relevantes entre variáveis distintas.")
        return

    var1, var2 = par
    intensidade = classificar_correlacao(valor)
    sentido = direcao(valor)

    st.markdown(f"""
A maior correlação **entre variáveis distintas** é **{valor:.2f}**,  
entre **{var1}** e **{var2}**.  

Essa relação pode ser classificada como **{intensidade}** e **{sentido}**.
""")
