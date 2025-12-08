# ============================================================
# PyTab - Fase MEDIR
# ============================================================
# Entregas desta fase:
# - Escolha do indicador numérico
# - Detecção automática da coluna de data
# - Agregação temporal (D / W / M / Q / Y)
# - Cartões de estatísticas descritivas
# - Gráfico de tendência + média móvel + meta
# - Detecção e visualização de outliers
# ============================================================

from __future__ import annotations

import pandas as pd
import streamlit as st

from pytab_app.modules.aggregation import (
    detect_date_column,
    aggregate_series,
)
from pytab_app.fases.medir.stats_cards import mostrar_stats_cards
from pytab_app.modules.trend_plot import render_trend_section
from pytab_app.modules.outliers import render_outliers_section


# ------------------------------------------------------------
# Função principal da fase MEDIR
# ------------------------------------------------------------
def fase_medir(df: pd.DataFrame):
    st.header("📏 Fase Medir — Estatísticas e Comportamento do Indicador")

    # 1) Colunas numéricas disponíveis
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.error("Nenhuma coluna numérica encontrada no dataset.")
        return

    indicador = st.selectbox(
        "Selecione o indicador numérico que você deseja analisar",
        options=numeric_cols,
    )

    # 2) Detectar automaticamente a coluna de data
    date_col = detect_date_column(df)

    if date_col is None:
        st.error(
            "Nenhuma coluna de data foi identificada automaticamente.\n\n"
            "A Fase Medir exige pelo menos uma coluna temporal para análise de série histórica."
        )
        return

    st.markdown(f"**Coluna de data identificada:** `{date_col}`")

    # 3) Configurações de agregação temporal
    st.subheader("⚙️ Configurações da série temporal")

    col1, col2 = st.columns(2)
    with col1:
        freq_label = st.selectbox(
            "Agrupamento temporal",
            options=["Diário", "Semanal", "Mensal", "Trimestral", "Anual"],
            index=2,  # Mensal como padrão
        )

    with col2:
        mostrar_preview = st.checkbox(
            "Mostrar prévia da série agregada",
            value=True,
        )

    # 4) Agregar a série temporal
    try:
        serie = aggregate_series(df, date_col, indicador, freq_label)
    except Exception as e:
        st.error(f"Erro ao agregar a série temporal: {e}")
        return

    if serie is None or serie.empty:
        st.warning("A série temporal agregada está vazia após o processamento.")
        return

    # 5) Prévia dos dados agregados
    if mostrar_preview:
        st.markdown("### 🔎 Prévia da série temporal agregada")
        st.dataframe(
            serie.to_frame(name=indicador).head(),
            use_container_width=True,
        )

    # 6) Cartões de estatísticas descritivas
    st.subheader("📊 Estatísticas descritivas")
    mostrar_stats_cards(serie, indicador)

    # 7) Gráfico de tendência + narrativa automática
    render_trend_section(serie, indicador)

    # 8) Outliers (boxplot, série, tabela, narrativa)
    render_outliers_section(serie, indicador)

