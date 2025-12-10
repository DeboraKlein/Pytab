"""
Fase MEDIR do PyTab — Lean Six Sigma
------------------------------------

Fluxo da fase Medir:

1. Seleção do indicador (coluna numérica)
2. Seleção da coluna de data
3. Agregação temporal automática ou definida pelo usuário
4. Exibição de estatísticas descritivas
5. Gráfico de tendência com média móvel opcional
6. Boxplot para distribuição
7. Detecção de outliers (Z-score, IQR, MAD ou Automático)
8. Tabela + gráfico dos outliers
"""

import streamlit as st
import pandas as pd
import numpy as np

from pytab_app.modules.aggregation import aggregate_series, detect_date_column
from pytab_app.modules.trend_plot import plot_tendencia
from pytab_app.modules.outliers import detectar_outliers
from pytab_app.fases.medir.visoes import grafico_boxplot, grafico_outliers


# ==========================================================
# 1. Estatísticas descritivas (para cards)
# ==========================================================

def calcular_estatisticas(series: pd.Series):
    s = series.dropna()
    stats = {
        "Média": s.mean(),
        "Mediana": s.median(),
        "Desvio Padrão": s.std(ddof=1),
        "Mínimo": s.min(),
        "Máximo": s.max(),
        "Amplitude": s.max() - s.min(),
        "CV (%)": (s.std(ddof=1) / s.mean() * 100) if s.mean() != 0 else np.nan,
    }
    return stats


def exibir_cards(stats: dict):
    st.subheader(" Estatísticas Descritivas")

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("Média", f"{stats['Média']:.2f}")
    col2.metric("Mediana", f"{stats['Mediana']:.2f}")
    col3.metric("Desvio Padrão", f"{stats['Desvio Padrão']:.2f}")

    col4.metric("Mínimo", f"{stats['Mínimo']:.2f}")
    col5.metric("Máximo", f"{stats['Máximo']:.2f}")
    col6.metric("CV (%)", f"{stats['CV (%)']:.2f}")


# ==========================================================
# 2. FASE MEDIR — PRINCIPAL
# ==========================================================

def fase_medir(df: pd.DataFrame):

    st.header(" Fase Medir — Compreensão do Indicador")

    # ------------------------------------------------------
    #  Escolha do indicador
    # ------------------------------------------------------
    numeric_cols = df.select_dtypes(include=["number", "float", "int"]).columns.tolist()

    if not numeric_cols:
        st.error("Nenhuma coluna numérica encontrada no dataset.")
        return

    indicador = st.selectbox("Selecione o indicador a analisar", numeric_cols)

    # ------------------------------------------------------
    #  Escolha da coluna de datas
    # ------------------------------------------------------
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    if not date_cols:
        st.error("Nenhuma coluna de datas encontrada no arquivo. A fase Medir exige datas.")
        return

    coluna_data = st.selectbox("Selecione a coluna de datas", date_cols)

    # ------------------------------------------------------
    #  Configurações de agregação e média móvel
    # ------------------------------------------------------
    st.subheader("⚙ Configurações da Série Temporal")

    colA, colB, colC = st.columns(3)

    with colA:
        periodicidade = st.selectbox(
            "Periodicidade",
            ["Diário", "Semanal", "Mensal", "Trimestral", "Anual"],
            index=2
        )

    with colB:
        usar_mm = st.checkbox("Incluir Média Móvel", value=True)

    with colC:
        janela = st.number_input(
            "Janela da Média Móvel",
            value=7,
            min_value=2,
            max_value=90
        )

    # ------------------------------------------------------
    #  Agregação Temporal
    # ------------------------------------------------------
    df_agregado = aggregate_series(df, coluna_data, indicador, periodicidade)

    # ------------------------------------------------------
    #  Estatísticas descritivas
    # ------------------------------------------------------
    stats = calcular_estatisticas(df[indicador])
    exibir_cards(stats)

    # ------------------------------------------------------
    #  Gráfico principal (série temporal)
    # ------------------------------------------------------
    st.subheader(" Tendência do Indicador")

    fig_trend = plot_tendencia(
        df_agregado,
        rolling_window=janela if usar_mm else None
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    # ------------------------------------------------------
    #  Boxplot da distribuição
    # ------------------------------------------------------
    st.subheader(" Distribuição dos Valores (Boxplot)")

    fig_box = grafico_boxplot(df, indicador)
    st.plotly_chart(fig_box, use_container_width=True)

    # ------------------------------------------------------
    #  Outliers
    # ------------------------------------------------------
    st.subheader(" Detecção de Outliers")

    metodo = st.selectbox("Método de detecção", ["Automático", "Z-score", "IQR", "MAD"])

    outliers, info = detectar_outliers(df[indicador], metodo=metodo)

    # Tabela
    st.write(f"**Outliers encontrados: {len(outliers)} valores**")
    st.dataframe(outliers.reset_index().rename(columns={"index": "Linha", indicador: "Valor"}))

    # Gráfico
    fig_o = grafico_outliers(df, indicador, outliers)
    st.plotly_chart(fig_o, use_container_width=True)

    # ------------------------------------------------------
    #  Nota sobre agregação e outliers
    # ------------------------------------------------------
    st.info("""
⚠ **Importante:** Para detecção de outliers, o PyTab sempre utiliza os valores originais.
A agregação temporal (mensal, semanal etc.) é aplicada **apenas** para facilitar a visualização da tendência.
    """)


