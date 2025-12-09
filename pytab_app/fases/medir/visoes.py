"""
Visões da Fase Medir (gráficos e tabelas).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly


def grafico_boxplot(df: pd.DataFrame, indicador: str):
    s = pd.to_numeric(df[indicador], errors="coerce").dropna()

    fig = px.box(s, points="all", title=f"Distribuição — {indicador}")
    fig.update_traces(marker_color=PRIMARY)

    return style_plotly(fig)


def grafico_outliers(df: pd.DataFrame, indicador: str, outliers):
    s = pd.to_numeric(df[indicador], errors="coerce").dropna()

    o_values = outliers.index
    o_points = outliers.values

    fig = go.Figure()

    # Série original
    fig.add_trace(go.Scatter(
        x=s.index,
        y=s.values,
        mode="lines",
        name="Valores originais",
        line=dict(color=PRIMARY, width=2),
    ))

    # Pontos de outlier
    fig.add_trace(go.Scatter(
        x=o_values,
        y=o_points,
        mode="markers",
        name="Outliers",
        marker=dict(color=SECONDARY, size=10),
    ))

    fig.update_layout(
        title=f"Outliers — {indicador}",
        xaxis_title="Índice (ordem)",
        yaxis_title="Valor",
    )

    return style_plotly(fig)
