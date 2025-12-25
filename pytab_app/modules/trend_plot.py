""""
Gráfico principal de tendência para a Fase Medir.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly


def _to_series(df_or_series: pd.DataFrame | pd.Series) -> pd.Series:
    """
    Normaliza a entrada para uma pd.Series indexada por data/tempo.
    Aceita:
      - Series com index temporal
      - DataFrame com 1 coluna datetime + 1 coluna numérica
      - DataFrame já indexado por datetime com 1+ colunas numéricas (usa a 1ª)
    """
    if isinstance(df_or_series, pd.Series):
        return df_or_series.dropna()

    df = df_or_series.copy()

    # Caso 1: índice já é datetime
    if isinstance(df.index, pd.DatetimeIndex):
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if not num_cols:
            raise ValueError("plot_tendencia: DataFrame indexado por data, mas sem coluna numérica.")
        return df[num_cols[0]].dropna()

    # Caso 2: existe coluna datetime
    date_cols = df.select_dtypes(
        include=["datetime64[ns]", "datetime64[ns, UTC]", "datetimetz"]
    ).columns.tolist()

    if not date_cols:
        # fallback: tenta converter a primeira coluna para datetime
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        date_cols = [date_col]

    date_col = date_cols[0]

    num_cols = df.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        raise ValueError("plot_tendencia: não encontrou coluna numérica para plotar.")
    value_col = num_cols[0]

    df = df.dropna(subset=[date_col, value_col]).sort_values(date_col)
    s = df.set_index(date_col)[value_col]
    return s.dropna()


def plot_tendencia(df_temp: pd.DataFrame | pd.Series, rolling_window: int | None = None):
    """
    df_temp → série agregada por período (Series) OU DataFrame com data + valor
    rolling_window → janela para média móvel (opcional)
    """
    s = _to_series(df_temp)

    fig = go.Figure()

    # Série temporal agregada
    fig.add_trace(
        go.Scatter(
            x=s.index,
            y=s.values,
            mode="lines+markers",
            name="Valor médio agregado",
            line=dict(color=PRIMARY, width=2),
            marker=dict(color=PRIMARY),
        )
    )

    # Média móvel opcional (somente sobre a série numérica)
    if rolling_window is not None and int(rolling_window) >= 2:
        roll = s.rolling(int(rolling_window), min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=roll.index,
                y=roll.values,
                mode="lines",
                name=f"Média móvel ({rolling_window})",
                line=dict(color=SECONDARY, width=2, dash="dash"),
            )
        )

    fig.update_layout(
        title="Série Temporal do Indicador",
        xaxis_title="Tempo",
        yaxis_title="Valor",
    )

    return style_plotly(fig)
