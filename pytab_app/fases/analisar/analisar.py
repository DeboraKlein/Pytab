import streamlit as st
import pandas as pd

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

    st.markdown("""
Nesta fase buscamos identificar **relações importantes**, **categorias que concentram impacto**  
e **dependências entre variáveis**.
""")

    st.divider()
    st.subheader("1. Correlação")
    resumo_corr = analisar_correlacao(df)

    st.divider()
    st.subheader("2. Pareto")
    resumo_par = analisar_pareto(df)

    st.divider()
    st.subheader("3. Regressão Linear Simples")
    resumo_reg = analisar_regressao(df)

    st.divider()
    st.subheader("4. Resumo Geral da Fase Analisar")

    if resumo_corr:
        st.markdown("#### 🔷 Correlação")
        st.markdown(gerar_narrativa_correlacao(resumo_corr))

    if resumo_par:
        st.markdown("#### 🟧 Pareto")
        st.markdown(gerar_narrativa_pareto(resumo_par))

    if resumo_reg:
        st.markdown("#### 📈 Regressão")
        st.markdown(gerar_narrativa_regressao(resumo_reg))
