# ============================================================
# PyTab - Módulo de Detecção e Visualização de Outliers
# ============================================================
# Inclui:
# - Cálculo por Z-score
# - Boxplot com destaque
# - Scatter temporal com outliers em evidência
# - Tabela de outliers
# - Narrativa automática
# ============================================================

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import streamlit as st

PRIMARY_BLUE = "#1f77b4"
SECONDARY_ORANGE = "#ec7f00"
TEXT_COLOR = "#333333"
BG_COLOR = "#f5f5f5"
OUTLIER_RED = "#d62728"


# ------------------------------------------------------------
# Função principal de detecção
# ------------------------------------------------------------
def detectar_outliers(series: pd.Series, z_limite: float = 2.5) -> pd.DataFrame:
    """
    Retorna DataFrame com:
    valor, zscore, é_outlier
    """

    media = series.mean()
    std = series.std()

    if std == 0 or np.isnan(std):
        return pd.DataFrame({
            "valor": series,
            "zscore": np.nan,
            "outlier": False,
        })

    zscores = (series - media) / std
    outliers = zscores.abs() > z_limite

    return pd.DataFrame({
        "valor": series,
        "zscore": zscores,
        "outlier": outliers,
    })


# ------------------------------------------------------------
# Boxplot com Plotly
# ------------------------------------------------------------
def plot_boxplot(series: pd.Series, results: pd.DataFrame, indicador: str):
    fig = go.Figure()

    fig.add_trace(go.Box(
        y=series,
        name=indicador,
        marker_color=PRIMARY_BLUE,
        boxpoints=False
    ))

    # Pontos de outliers (caso existam)
    out_data = results[results["outlier"]]

    if not out_data.empty:
        fig.add_trace(go.Scatter(
            x=["Outliers"] * len(out_data),
            y=out_data["valor"],
            mode="markers",
            name="Outliers",
            marker=dict(color=OUTLIER_RED, size=8),
        ))

    fig.update_layout(
        title=f"Boxplot — {indicador}",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        margin=dict(l=40, r=20, t=60, b=40)
    )

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)

    return fig


# ------------------------------------------------------------
# Scatter temporal com destaque
# ------------------------------------------------------------
def plot_temporal_outliers(series: pd.Series, results: pd.DataFrame, indicador: str):
    fig = go.Figure()

    # Linha normal
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        name="Série",
        line=dict(color=PRIMARY_BLUE, width=2)
    ))

    # Pontos de outliers
    out_data = results[results["outlier"]]
    if not out_data.empty:
        fig.add_trace(go.Scatter(
            x=out_data.index,
            y=out_data["valor"],
            mode="markers",
            name="Outliers",
            marker=dict(color=OUTLIER_RED, size=8),
        ))

    fig.update_layout(
        title=f"Série Temporal com Outliers — {indicador}",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        margin=dict(l=40, r=20, t=60, b=40)
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


# ------------------------------------------------------------
# Narrativa automática
# ------------------------------------------------------------
def gerar_narrativa(results: pd.DataFrame) -> str:
    total = len(results)
    qtd = results["outlier"].sum()

    if total == 0:
        return "Não foi possível avaliar outliers (série vazia)."

    pct = qtd / total * 100

    if qtd == 0:
        return "Nenhum outlier foi detectado. A série é consistente e não apresenta valores extremos significativos."

    msg = f"Foram detectados **{qtd} outliers**, representando **{pct:.1f}%** da série.\n\n"

    # Classificação simples
    if pct < 2:
        msg += "A presença de outliers é **muito baixa**, sugerindo que são casos isolados."
    elif pct < 10:
        msg += "A presença de outliers é **moderada**, sugerindo possíveis exceções ou anomalias pontuais."
    else:
        msg += "A presença de outliers é **alta**, indicando variabilidade incomum ou potenciais erros de registro."

    return msg


# ------------------------------------------------------------
# Função integrada para Streamlit
# ------------------------------------------------------------
def render_outliers_section(series: pd.Series, indicador: str):
    st.subheader("🔎 Detecção de Outliers")

    col1, col2 = st.columns(2)

    with col1:
        z_lim = st.number_input(
            "Limite do Z-score",
            min_value=1.0,
            max_value=5.0,
            value=2.5,
            step=0.1
        )

    # Detectar
    results = detectar_outliers(series, z_lim)

    # Gráficos
    st.markdown("### Boxplot")
    fig_box = plot_boxplot(series, results, indicador)
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("### Série Temporal com Outliers Destacados")
    fig_temp = plot_temporal_outliers(series, results, indicador)
    st.plotly_chart(fig_temp, use_container_width=True)

    # Tabela
    st.markdown("### Tabela de Outliers")
    st.dataframe(results[results["outlier"]])

    # Narrativa
    st.markdown("### 🧠 Interpretação dos Outliers")
    st.info(gerar_narrativa(results))
