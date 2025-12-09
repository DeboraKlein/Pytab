# ============================================================
# PyTab - Fase MEDIR - Visões de Outliers
# ============================================================
# Usa:
#  - modules.outliers (Z-score, IQR, MAD, modo automático)
#  - Plotly para gráficos
#  - Streamlit para interface
# ============================================================

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pytab_app.modules.outliers import detect_outliers

PRIMARY_BLUE = "#1f77b4"
SECONDARY_ORANGE = "#ec7f00"
TEXT_COLOR = "#333333"
BG_COLOR = "#f5f5f5"
OUTLIER_RED = "#d62728"


def _build_boxplot(series: pd.Series, results: pd.DataFrame, indicador: str) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Box(
            y=series,
            name=indicador,
            marker_color=PRIMARY_BLUE,
            boxpoints=False,
        )
    )

    out_data = results[results["outlier"]]
    if not out_data.empty:
        fig.add_trace(
            go.Scatter(
                x=["Outliers"] * len(out_data),
                y=out_data["valor"],
                mode="markers",
                name="Outliers",
                marker=dict(color=OUTLIER_RED, size=8),
            )
        )

    fig.update_layout(
        title=f"Boxplot — {indicador}",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        margin=dict(l=40, r=20, t=60, b=40),
    )

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)

    return fig


def _build_scatter_time(
    x: pd.Series,
    series: pd.Series,
    results: pd.DataFrame,
    indicador: str,
) -> go.Figure:
    # Garante alinhamento de índices
    s = series
    mask = results["outlier"].reindex(s.index).fillna(False)

    fig = go.Figure()

    # Pontos normais
    fig.add_trace(
        go.Scatter(
            x=x[~mask],
            y=s[~mask],
            mode="markers",
            name="Valores dentro do padrão",
            marker=dict(color=PRIMARY_BLUE, size=6, opacity=0.5),
        )
    )

    # Outliers
    if mask.any():
        fig.add_trace(
            go.Scatter(
                x=x[mask],
                y=s[mask],
                mode="markers",
                name="Outliers",
                marker=dict(color=OUTLIER_RED, size=9),
        )
        )

    fig.update_layout(
        title=f"Série temporal (dados originais) — {indicador}",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        margin=dict(l=40, r=20, t=60, b=40),
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


def render_outliers_section(
    df: pd.DataFrame,
    indicador: str,
    date_col: str | None = None,
):
    """
    Renderiza a seção de outliers na Fase MEDIR usando a base original.
    df: DataFrame original (sem agregação)
    indicador: nome da coluna numérica
    date_col: nome da coluna de data (opcional, mas recomendado)
    """

    st.subheader(" Outliers do indicador (base original)")

    # Prepara série e eixo X
    if date_col and date_col in df.columns:
        df_local = df[[date_col, indicador]].copy()
        df_local[date_col] = pd.to_datetime(df_local[date_col], errors="coerce")
        df_local = df_local.dropna(subset=[date_col, indicador])
        df_local = df_local.sort_values(by=date_col)

        x = df_local[date_col]
        series = df_local[indicador].astype(float)
    else:
        series = df[indicador].dropna().astype(float)
        x = series.index

    if series.empty:
        st.warning("Não há dados suficientes para análise de outliers.")
        return

    # Escolha do método
    st.markdown("### Método de detecção de outliers")

    metodo_label = st.selectbox(
        "Selecione o método",
        options=[
            "Automático (recomendado)",
            "Z-score",
            "IQR (Interquartile Range)",
            "MAD (Median Absolute Deviation)",
        ],
    )

    method_key = "auto"
    if metodo_label.startswith("Z-score"):
        method_key = "zscore"
    elif metodo_label.startswith("IQR"):
        method_key = "iqr"
    elif metodo_label.startswith("MAD"):
        method_key = "mad"

    col1, col2, col3 = st.columns(3)

    with col1:
        z_lim = st.number_input(
            "Limite Z-score",
            min_value=1.0,
            max_value=5.0,
            value=2.5,
            step=0.1,
        )

    with col2:
        iqr_k = st.number_input(
            "Multiplicador IQR",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.1,
        )

    with col3:
        mad_thresh = st.number_input(
            "Limite MAD",
            min_value=1.0,
            max_value=10.0,
            value=3.5,
            step=0.5,
        )

    results, info = detect_outliers(
        series,
        method=method_key,
        z_lim=z_lim,
        iqr_k=iqr_k,
        mad_thresh=mad_thresh,
    )

    metodo_usado = info.get("method", "zscore")
    n = info.get("n", len(series))
    n_out = info.get("n_outliers", int(results["outlier"].sum()))
    auto_msg = info.get("auto_message", "")

    st.markdown(
        f"**Método efetivamente usado:** `{metodo_usado}`  "
        f"• **Dados avaliados:** {n}  "
        f"• **Outliers encontrados:** {n_out}"
    )
    if auto_msg:
        st.info(auto_msg)

    # Boxplot
    st.markdown("### Boxplot com destaque dos outliers")
    fig_box = _build_boxplot(series, results, indicador)
    st.plotly_chart(fig_box, use_container_width=True)

    # Série temporal original
    st.markdown("### Série temporal (dados originais) com outliers destacados")
    fig_scatter = _build_scatter_time(x, series, results, indicador)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Tabela de outliers
    st.markdown("### Tabela de outliers (base original)")
    mask = results["outlier"]
    if mask.any():
        df_out = pd.DataFrame(
            {
                "Data": x[mask],
                indicador: series[mask],
                "Score": results["score"][mask],
            }
        )
        st.dataframe(df_out.sort_values(by="Data"), use_container_width=True)
    else:
        st.info("Nenhum outlier foi identificado com o método e parâmetros atuais.")

    # Nota educativa sobre agregação
    st.caption(
        "Observação: a detecção de outliers é feita **sempre na base original**, "
        "independentemente do agrupamento temporal usado nos gráficos de tendência. "
        "Isso evita que valores extremos sejam 'escondidos' pela média."
    )
