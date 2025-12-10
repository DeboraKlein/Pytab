import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly
from .narrativas import gerar_narrativa_regressao


def analisar_regressao(df: pd.DataFrame) -> dict | None:
    """
    Regressão linear simples (Y em função de X) com narrativa.
    """

    st.subheader("Regressão linear simples")

    numeric_cols = df.select_dtypes(include=["number", "float", "int"]).columns.tolist()
    if len(numeric_cols) < 2:
        st.info("É necessário ter pelo menos duas colunas numéricas para regressão.")
        return None

    col_y = st.selectbox("Selecione a variável dependente (Y)", numeric_cols)
    possiveis_x = [c for c in numeric_cols if c != col_y]

    if not possiveis_x:
        st.info("Selecione outra combinação de variáveis para regressão.")
        return None

    col_x = st.selectbox("Selecione a variável explicativa (X)", possiveis_x)

    df_xy = df[[col_x, col_y]].dropna()
    if len(df_xy) < 2:
        st.warning("Não há dados suficientes para ajustar o modelo.")
        return None

    x = df_xy[col_x].values.astype(float)
    y = df_xy[col_y].values.astype(float)

    # Ajuste da reta (y = a*x + b)
    a, b = np.polyfit(x, y, 1)
    y_pred = a * x + b

    # Cálculo de R²
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan

    # Gráfico
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name="Dados observados",
            marker=dict(color=PRIMARY, size=7, opacity=0.8),
        )
    )

    # Linha de regressão (ordenando x para linha ficar bonita)
    ordem = np.argsort(x)
    fig.add_trace(
        go.Scatter(
            x=x[ordem],
            y=y_pred[ordem],
            mode="lines",
            name="Linha de regressão",
            line=dict(color=SECONDARY, width=2),
        )
    )

    fig.update_layout(
        title=f"{col_y} em função de {col_x}",
        xaxis_title=col_x,
        yaxis_title=col_y,
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
**Equação aproximada do modelo:**

{col_y} ≈ {a:.3f} · {col_x} + {b:.3f}  
R² ≈ {r2:.3f}
"""
    )

    summary = {
        "x": col_x,
        "y": col_y,
        "coef_angular": float(a),
        "intercepto": float(b),
        "r2": float(r2),
    }

    texto = gerar_narrativa_regressao(summary)
    st.markdown(texto)

    return summary
