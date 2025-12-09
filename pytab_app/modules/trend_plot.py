"""
Gráfico principal de tendência para a Fase Medir.
"""

import pandas as pd
import plotly.graph_objects as go
from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly


def plot_tendencia(df_temp: pd.Series, rolling_window: int | None = None):
    """
    df_temp → série agregada por período
    rolling_window → janela para média móvel (opcional)
    """

    fig = go.Figure()

    # Série temporal agregada
    fig.add_trace(go.Scatter(
        x=df_temp.index,
        y=df_temp.values,
        mode="lines+markers",
        name="Valor médio agregado",
        line=dict(color=PRIMARY, width=2),
        marker=dict(color=PRIMARY),
    ))

    # Média móvel opcional
    if rolling_window:
        roll = df_temp.rolling(rolling_window).mean()
        fig.add_trace(go.Scatter(
            x=roll.index,
            y=roll.values,
            mode="lines",
            name=f"Média móvel ({rolling_window})",
            line=dict(color=SECONDARY, width=2, dash="dash"),
        ))

    fig.update_layout(
        title="Série Temporal do Indicador",
        xaxis_title="Tempo",
        yaxis_title="Valor",
    )

    return style_plotly(fig)

