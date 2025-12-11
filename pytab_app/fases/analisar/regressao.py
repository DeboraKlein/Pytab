import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly


def analisar_regressao(df: pd.DataFrame) -> None:
    """
    Regressão linear simples (Y ~ X) com narrativa automática.
    """
    st.subheader("Regressão Linear Simples")

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(num_cols) < 2:
        st.info("É necessário pelo menos duas colunas numéricas para rodar regressão.")
        return

    col_y = st.selectbox("Variável alvo (Y)", num_cols)
    col_x = st.selectbox(
        "Variável explicativa (X)",
        [c for c in num_cols if c != col_y],
    )

    dados = df[[col_x, col_y]].dropna()
    if dados.shape[0] < 3:
        st.warning("Poucos pontos de dados para ajustar uma regressão confiável.")
        return

    x = dados[col_x].to_numpy(dtype=float)
    y = dados[col_y].to_numpy(dtype=float)

    x_mean = x.mean()
    y_mean = y.mean()

    cov = ((x - x_mean) * (y - y_mean)).sum()
    var_x = ((x - x_mean) ** 2).sum()

    if var_x == 0:
        st.warning("A variável X não varia (variância zero). Não é possível ajustar regressão.")
        return

    slope = cov / var_x
    intercept = y_mean - slope * x_mean
    y_pred = slope * x + intercept

    ss_tot = ((y - y_mean) ** 2).sum()
    ss_res = ((y - y_pred) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    # Gráfico
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(color=PRIMARY, size=7),
            name="Dados observados",
        )
    )
    # ordenar X para a linha ficar “bonita”
    ordem = np.argsort(x)
    fig.add_trace(
        go.Scatter(
            x=x[ordem],
            y=y_pred[ordem],
            mode="lines",
            line=dict(color=SECONDARY, width=2),
            name="Reta ajustada",
        )
    )

    fig.update_layout(
        title=f"{col_y} em função de {col_x}",
        xaxis_title=col_x,
        yaxis_title=col_y,
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    # Narrativa
    st.markdown(f"""
### Resumo da regressão

- Equação estimada: **{col_y} ≈ {slope:.3f} × {col_x} + {intercept:.3f}**  
- Coeficiente de determinação (R²): **{r2:.3f}**

**Interpretação:**  
Para cada aumento de 1 unidade em **{col_x}**, o modelo estima um aumento médio de
**{slope:.3f}** unidades em **{col_y}**, em média.
""")

