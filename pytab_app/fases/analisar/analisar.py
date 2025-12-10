"""
Fase ANALISAR do PyTab — Lean Six Sigma

Objetivo:
- Entender relações entre variáveis
- Identificar concentrações de impacto (Pareto)
- Avaliar relações lineares simples (regressão)
"""

import pandas as pd
import streamlit as st

from .correlacao import analisar_correlacao
from .pareto import analisar_pareto
from .regressao import analisar_regressao
from .narrativas import (
    gerar_narrativa_correlacao,
    gerar_narrativa_pareto,
    gerar_narrativa_regressao,
)


def fase_analisar(df: pd.DataFrame):
    st.header("Fase Analisar — Relações e Causas Prováveis")

    st.markdown(
        "Nesta fase, o objetivo é entender **como as variáveis se relacionam** entre si "
        "e quais dimensões concentram a maior parte do impacto. "
        "Use os blocos abaixo para explorar correlações, Pareto e regressão simples."
    )

    # ======================================================
    # 1. Correlação
    # ======================================================
    st.divider()
    st.markdown("### 1. Correlação entre variáveis")
    resumo_corr = analisar_correlacao(df)

    # ======================================================
    # 2. Pareto
    # ======================================================
    st.divider()
    st.markdown("### 2. Análise de Pareto")
    resumo_par = analisar_pareto(df)

    # ======================================================
    # 3. Regressão linear simples
    # ======================================================
    st.divider()
    st.markdown("### 3. Regressão linear simples")
    resumo_reg = analisar_regressao(df)

    # ======================================================
    # 4. Resumo textual da fase Analisar
    # ======================================================
    st.divider()
    st.markdown("### 4. Resumo textual da análise")

    # Gera um pequeno painel de resumo, usando os últimos resultados
    textos = []

    textos.append(gerar_narrativa_correlacao(resumo_corr))
    textos.append(gerar_narrativa_pareto(resumo_par))
    textos.append(gerar_narrativa_regressao(resumo_reg))

    for t in textos:
        st.markdown(f"- {t}")
