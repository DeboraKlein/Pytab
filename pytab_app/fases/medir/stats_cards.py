# pytab_app/fases/medir/stats_cards.py

import streamlit as st
import pandas as pd
import numpy as np


# -----------------------------------------------------------
# INTERPRETAÇÃO AUTOMÁTICA DAS ESTATÍSTICAS
# -----------------------------------------------------------

def interpretar_cv(cv: float) -> str:
    """Fornece interpretação do coeficiente de variação."""
    if cv < 5:
        return "Muito estável (variação mínima)."
    if cv < 15:
        return "Estável, com leve oscilação."
    if cv < 30:
        return "Moderadamente variável."
    if cv < 50:
        return "Alta variabilidade - investigar causas."
    return "Extremamente variável - comportamento imprevisível."


def interpretar_trend(delta: float) -> str:
    """Interpreta variação percentual mês a mês."""
    if delta > 20:
        return "Crescimento acentuado no período."
    if delta > 5:
        return "Tendência de aumento."
    if delta > -5:
        return "Estabilidade no período."
    if delta > -20:
        return "Tendência de queda."
    return "Queda acentuada no período."


# -----------------------------------------------------------
# GERAÇÃO DOS CARTÕES DE ESTATÍSTICAS
# -----------------------------------------------------------

def mostrar_stats_cards(series: pd.Series, nome_indicador: str):
    """
    Gera cartões estilo Power BI contendo:
    • Média
    • Mediana
    • Desvio Padrão
    • CV (%)
    • Variação % período a período
    """

    st.subheader(" Estatísticas principais do indicador")

    if len(series) < 3:
        st.warning("Série temporal muito curta para análises estatísticas.")
        return

    media = series.mean()
    mediana = series.median()
    std = series.std()
    cv = (std / media) * 100 if media != 0 else np.nan

    # Variação percentual mês-a-mês
    delta = ((series.iloc[-1] - series.iloc[-2]) / abs(series.iloc[-2])) * 100

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Média",
            value=f"{media:,.2f}",
        )

    with col2:
        st.metric(
            label="Mediana",
            value=f"{mediana:,.2f}",
        )

    with col3:
        st.metric(
            label="Desvio Padrão",
            value=f"{std:,.2f}",
        )

    with col4:
        st.metric(
            label="Coeficiente de Variação (CV)",
            value=f"{cv:,.1f}%",
        )

    # -----------------------------------------------------------
    # INTERPRETAÇÃO AUTOMÁTICA
    # -----------------------------------------------------------

    st.markdown("###  Interpretação automática")

    st.info(f"""
    **Estabilidade do indicador:** {interpretar_cv(cv)}

    **Variação recente:** {interpretar_trend(delta)}
    
    **Resumo matemático:**  
    • Média = {media:,.2f}  
    • Mediana = {mediana:,.2f}  
    • Desvio padrão = {std:,.2f}  
    • Variação recente = {delta:,.2f}%  
    """)

