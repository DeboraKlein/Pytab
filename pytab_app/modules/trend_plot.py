# ============================================================
# PyTab - Módulo de Tendência Temporal (Plotly)
# ============================================================
# Responsável por:
# - Plotar série temporal agregada
# - Aplicar média móvel
# - Exibir linha de target (meta)
# - Gerar narrativa automática:
#     • Estabilidade (via CV)
#     • Tendência (subida/queda)
#     • Relação com a meta
# ============================================================

from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go


# Paleta corporativa PyTab
PRIMARY_BLUE = "#1f77b4"
SECONDARY_ORANGE = "#ec7f00"
TEXT_COLOR = "#333333"
BG_COLOR = "#f5f5f5"


# ------------------------------------------------------------
# Funções auxiliares de análise
# ------------------------------------------------------------

def _coeficiente_variacao(series: pd.Series) -> float:
    """Retorna CV em %."""
    media = series.mean()
    std = series.std()
    if media == 0 or np.isnan(media):
        return np.nan
    return (std / media) * 100.0


def _interpretar_cv(cv: float) -> str:
    """Texto de interpretação da estabilidade via CV."""
    if np.isnan(cv):
        return "Não foi possível calcular a estabilidade (CV indefinido)."

    if cv < 5:
        return "O indicador é **muito estável**, com variação mínima."
    if cv < 15:
        return "O indicador é **estável**, com leve oscilação."
    if cv < 30:
        return "O indicador apresenta **variação moderada**."
    if cv < 50:
        return "O indicador tem **alta variabilidade** – vale investigar causas."
    return "O indicador é **extremamente variável** – comportamento pouco previsível."


def _tendencia_geral(series: pd.Series) -> tuple[str, float]:
    """
    Calcula tendência geral simples via variação percentual
    entre primeiro e último ponto.
    Retorna (texto, delta_pct).
    """
    if len(series) < 2:
        return "Série muito curta para avaliar tendência.", np.nan

    inicio = series.iloc[0]
    fim = series.iloc[-1]

    if inicio == 0:
        return "Não foi possível calcular tendência (valor inicial zero).", np.nan

    delta_pct = (fim - inicio) / abs(inicio) * 100.0

    if delta_pct > 20:
        txt = "Tendência de **alta acentuada** ao longo do período."
    elif delta_pct > 5:
        txt = "Tendência de **alta gradual** ao longo do período."
    elif delta_pct > -5:
        txt = "O indicador se mantém **relativamente estável** ao longo do período."
    elif delta_pct > -20:
        txt = "Tendência de **queda gradual** ao longo do período."
    else:
        txt = "Tendência de **queda acentuada** ao longo do período."

    return txt, delta_pct


def _interpretar_meta(series: pd.Series, target: float | None) -> str:
    """Compara média da série com a meta (quando informada)."""
    if target is None:
        return "Nenhuma meta foi informada para comparação."

    media = series.mean()

    if np.isnan(media):
        return "Não foi possível comparar com a meta (média indefinida)."

    if media > target * 1.05:
        return f"A média do indicador (**{media:,.2f}**) está **acima da meta** ({target:,.2f})."
    elif media < target * 0.95:
        return f"A média do indicador (**{media:,.2f}**) está **abaixo da meta** ({target:,.2f})."
    else:
        return f"A média do indicador (**{media:,.2f}**) está **próxima da meta** ({target:,.2f})."


# ------------------------------------------------------------
# Função pura de plotar tendência (sem Streamlit)
# ------------------------------------------------------------

def plot_trend(
    series: pd.Series,
    rolling: pd.Series | None = None,
    target: float | None = None,
    indicador: str = "Indicador",
) -> go.Figure:
    """
    Cria figura Plotly com:
    - série temporal principal
    - média móvel (opcional)
    - linha de target (opcional)
    """

    fig = go.Figure()

    # Série principal
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines",
            name="Valor médio",
            line=dict(color=PRIMARY_BLUE, width=2),
        )
    )

    # Média móvel
    if rolling is not None:
        fig.add_trace(
            go.Scatter(
                x=rolling.index,
                y=rolling.values,
                mode="lines",
                name="Média móvel",
                line=dict(color=SECONDARY_ORANGE, width=2, dash="dash"),
            )
        )

    # Linha de meta (target)
    if target is not None:
        fig.add_trace(
            go.Scatter(
                x=[series.index.min(), series.index.max()],
                y=[target, target],
                mode="lines",
                name="Meta",
                line=dict(color="#999999", width=2, dash="dot"),
            )
        )

    fig.update_layout(
        title=f"Tendência temporal — {indicador}",
        xaxis_title="Tempo",
        yaxis_title=indicador,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0.0,
        ),
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        margin=dict(l=40, r=20, t=60, b=60),
    )

    # Eixos sem grid visual
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


# ------------------------------------------------------------
# Seção integrada para uso no Streamlit
# ------------------------------------------------------------

def render_trend_section(
    series: pd.Series,
    indicador: str,
    default_window: int = 7,
):
    """
    Renderiza no Streamlit:
    - controles (janela média móvel, target)
    - gráfico de tendência
    - narrativa automática
    """

    st.subheader(" Comportamento temporal do indicador")

    if len(series) < 3:
        st.warning("Série temporal muito curta para análise de tendência.")
        return

    col1, col2 = st.columns(2)

    with col1:
        usar_mm = st.checkbox("Incluir média móvel", value=True)
        if usar_mm:
            janela = st.number_input(
                "Janela da média móvel",
                min_value=2,
                max_value=max(2, min(60, len(series))),
                value=min(default_window, len(series)),
                step=1,
            )
        else:
            janela = None

    with col2:
        target_input = st.text_input(
            "Meta (target) opcional",
            value="",
            help="Informe um número para traçar uma linha de meta. Deixe em branco para ignorar.",
        )
        target = None
        if target_input.strip():
            try:
                target = float(target_input.replace(",", "."))
            except ValueError:
                st.warning("Meta inválida. Use apenas números (ponto como separador decimal).")
                target = None

    # Média móvel (se habilitada)
    if janela is not None:
        rolling = series.rolling(janela, min_periods=1).mean()
    else:
        rolling = None

    # Gráfico
    fig = plot_trend(series, rolling=rolling, target=target, indicador=indicador)
    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # NARRATIVA AUTOMÁTICA
    # --------------------------------------------------------
    st.markdown("### Interpretação automática da tendência")

    cv = _coeficiente_variacao(series)
    texto_cv = _interpretar_cv(cv)
    texto_tendencia, delta = _tendencia_geral(series)
    texto_meta = _interpretar_meta(series, target)

    st.info(
        f"""
**Estabilidade (CV):** {texto_cv}  

**Tendência geral:** {texto_tendencia}  
{"" if np.isnan(delta) else f"_Variação aproximada entre início e fim: {delta:,.2f}%._"}  

**Relação com a meta:** {texto_meta}
"""
    )
