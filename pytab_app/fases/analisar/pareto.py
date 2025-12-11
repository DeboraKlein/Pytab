import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pytab.charts.theme import PRIMARY, SECONDARY, style_plotly


def analisar_pareto(df: pd.DataFrame):
    """
    Renderiza a análise de Pareto na aba correspondente.

    - Usuário escolhe uma dimensão categórica e uma métrica numérica
    - Exibe gráfico de Pareto (barras + linha de % acumulado)
    - Exibe narrativa automática em texto
    """
    st.subheader("Análise de Pareto")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not cat_cols or not num_cols:
        st.info("É necessário ao menos uma coluna categórica e uma numérica para a análise de Pareto.")
        return None

    col_cat = st.selectbox("Dimensão (categórica)", cat_cols)
    col_val = st.selectbox("Métrica (numérica)", num_cols)

    dados = df[[col_cat, col_val]].dropna()
    if dados.empty:
        st.warning("Não há dados suficientes após remoção de valores ausentes.")
        return None

    serie = (
        dados.groupby(col_cat)[col_val]
        .sum()
        .sort_values(ascending=False)
    )

    if serie.empty:
        st.warning("Não foi possível calcular a distribuição de Pareto para esta combinação.")
        return None

    total = serie.sum()
    perc = serie / total * 100.0
    cum = perc.cumsum()

    # ---------------------------
    # Gráfico Pareto (Plotly)
    # ---------------------------
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    categorias = serie.index.astype(str)

    fig.add_trace(
        go.Bar(
            x=categorias,
            y=serie.values,
            name="Valor",
            marker_color=PRIMARY,
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=categorias,
            y=cum.values,
            name="% acumulado",
            mode="lines+markers",
            line=dict(color=SECONDARY, width=3),
        ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text="Valor", secondary_y=False)
    fig.update_yaxes(
        title_text="% acumulado",
        range=[0, 110],
        secondary_y=True,
        showgrid=False,
    )

    fig.update_layout(
        title=f"Pareto de {col_val} por {col_cat}",
        xaxis_title=col_cat,
        bargap=0.15,
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # Narrativa automática
    # ---------------------------
    # Regra 80/20 aproximada
    n_top = (cum <= 80).sum()
    if n_top == 0:
        n_top = 1
    top_cats = serie.index[:n_top].tolist()
    share = float(cum.iloc[n_top - 1])

    st.markdown(_narrativa_pareto(col_cat, col_val, top_cats, share))

    # Retorna um resumo técnico (se quiser reaproveitar depois)
    return {
        "dimensao": col_cat,
        "metricao": col_val,
        "top_categorias": top_cats,
        "top_share": share,
        "n_top": int(n_top),
    }


def _narrativa_pareto(col_cat: str, col_val: str, top_cats, share: float) -> str:
    """Gera texto em português explicando o resultado do Pareto."""
    if not top_cats:
        return "Não foi possível identificar categorias dominantes para esta métrica."

    lista_str = ", ".join(str(c) for c in top_cats)

    return f"""
### Narrativa — Análise de Pareto

As categorias **{lista_str}** concentram aproximadamente **{share:.1f}%** do total de **{col_val}**
quando analisadas por **{col_cat}**.

Isso sugere que focar nessas categorias tende a gerar o maior impacto na melhoria do processo,
seguindo o princípio de Pareto (foco nos poucos vitais).
"""
