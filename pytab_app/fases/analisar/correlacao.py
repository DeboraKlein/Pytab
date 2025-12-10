import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from pytab.charts.theme import style_plotly
from .narrativas import gerar_narrativa_correlacao


def analisar_correlacao(df: pd.DataFrame):
    st.subheader("Correlação entre variáveis")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_cols) < 2:
        st.info("É necessário ter pelo menos duas colunas numéricas.")
        return None

    cols = st.multiselect(
        "Selecione as variáveis:",
        numeric_cols,
        default=numeric_cols[: min(4, len(numeric_cols))]
    )

    if len(cols) < 2:
        return None

    data = df[cols].dropna()
    corr = data.corr()

    # Heatmap confiável
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu",
            zmid=0,
            text=corr.round(2).values,
            texttemplate="%{text}",
            showscale=True,
        )
    )

    fig.update_layout(title="Matriz de Correlação", xaxis=dict(side="top"))
    fig = style_plotly(fig)

    st.plotly_chart(fig, use_container_width=True)

    # Identificação da maior correlação (somente triângulo superior)
    corr_abs = corr.abs()
    mask = np.tril(np.ones(corr_abs.shape)).astype(bool)
    corr_upper = corr_abs.where(~mask)

    max_pos = corr_upper.unstack().idxmax()
    var1, var2 = max_pos
    corr_val = corr.loc[var1, var2]

    summary = {
        "var1": var1,
        "var2": var2,
        "corr": corr_val
    }

    st.markdown(gerar_narrativa_correlacao(summary))

    return summary
