import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly
from .narrativas import gerar_narrativa_pareto


def analisar_pareto(df: pd.DataFrame) -> dict | None:
    """
    Renderiza a análise de Pareto e retorna um resumo para narrativas.
    """

    st.subheader("Análise de Pareto")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = df.select_dtypes(include=["number", "float", "int"]).columns.tolist()

    if not cat_cols or not num_cols:
        st.info("É necessário ter pelo menos uma coluna categórica e uma numérica para o Pareto.")
        return None

    col_cat = st.selectbox("Selecione a dimensão (categoria)", cat_cols)
    col_val = st.selectbox("Selecione a métrica (valor)", num_cols)

    df_aux = df[[col_cat, col_val]].dropna()
    if df_aux.empty:
        st.warning("Não há dados suficientes para esta combinação de colunas.")
        return None

    # Agregação por categoria
    serie = df_aux.groupby(col_cat)[col_val].sum().sort_values(ascending=False)
    total = serie.sum()
    if total == 0:
        st.warning("A soma dos valores é zero; não é possível montar o Pareto.")
        return None

    perc = serie / total
    cum_perc = perc.cumsum()

    pareto_df = pd.DataFrame(
        {
            "Categoria": serie.index,
            "Valor": serie.values,
            "Percentual": perc.values * 100,
            "Percentual acumulado": cum_perc.values * 100,
        }
    )

    # Definir quantas categorias cobrem ~80%
    n_top = int((cum_perc <= 0.8).sum())
    if n_top == 0:
        n_top = 1
    top_cats = pareto_df["Categoria"].iloc[:n_top].tolist()
    top_share = pareto_df["Percentual acumulado"].iloc[n_top - 1]

    # Gráfico de Pareto
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras
    fig.add_trace(
        go.Bar(
            x=pareto_df["Categoria"],
            y=pareto_df["Valor"],
            name="Valor",
            marker_color=PRIMARY,
        ),
        secondary_y=False,
    )

    # Linha cumulativa
    fig.add_trace(
        go.Scatter(
            x=pareto_df["Categoria"],
            y=pareto_df["Percentual acumulado"],
            name="Percentual acumulado",
            mode="lines+markers",
            line=dict(color=SECONDARY, width=2),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=f"Pareto de {col_val} por {col_cat}",
        xaxis_title=col_cat,
        yaxis_title="Valor",
    )
    fig.update_yaxes(title_text="Percentual acumulado (%)", secondary_y=True)

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Tabela detalhada (ordenada por contribuição):")
    st.dataframe(pareto_df, use_container_width=True)

    summary = {
        "dimensao": col_cat,
        "metricao": col_val,
        "top_categorias": top_cats,
        "top_share": float(top_share),
        "n_top": int(n_top),
    }

    texto = gerar_narrativa_pareto(summary)
    st.markdown(texto)

    return summary
