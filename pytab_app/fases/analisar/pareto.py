import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly
from .narrativas import gerar_narrativa_pareto


def analisar_pareto(df: pd.DataFrame):

    st.subheader("Análise de Pareto")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not cat_cols or not num_cols:
        st.info("Selecione ao menos uma coluna categórica e uma numérica.")
        return None

    col_cat = st.selectbox("Dimensão", cat_cols)
    col_val = st.selectbox("Métrica", num_cols)

    d = df[[col_cat, col_val]].dropna()
    serie = d.groupby(col_cat)[col_val].sum().sort_values(ascending=False)

    total = serie.sum()
    perc = serie / total
    cum = perc.cumsum() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=serie.index,
            y=serie.values,
            name="Valor",
            marker_color=PRIMARY,
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=serie.index,
            y=cum,
            name="Percentual acumulado",
            mode="lines+markers",
            line=dict(color=SECONDARY, width=3),
        ),
        secondary_y=True
    )

    # remove linha estranha
    fig.update_yaxes(showgrid=False, zeroline=False, secondary_y=True)

    fig.update_layout(
        title=f"Pareto de {col_val} por {col_cat}",
        xaxis_title=col_cat,
        yaxis_title="Valor",
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    # identificar 80/20
    n_top = (cum <= 80).sum()
    top_cats = serie.index[:n_top].tolist()
    share = float(cum.iloc[n_top - 1])

    summary = {
        "dimensao": col_cat,
        "metricao": col_val,
        "top_categorias": top_cats,
        "top_share": share,
        "n_top": n_top,
    }

    st.markdown(gerar_narrativa_pareto(summary))

    return summary

