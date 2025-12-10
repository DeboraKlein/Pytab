import pandas as pd
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

    fig.update_layout(
        title="Matriz de Correlação",
        xaxis=dict(side="top")
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    # pega maior correlação
    tri = corr.where(~pd.np.tril(pd.np.ones(corr.shape)).astype(bool))
    max_pos = tri.unstack().abs().idxmax()

    summary = {
        "var1": max_pos[0],
        "var2": max_pos[1],
        "corr": corr.loc[max_pos[0], max_pos[1]]
    }

    st.markdown(gerar_narrativa_correlacao(summary))

    return summary
