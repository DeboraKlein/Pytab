from __future__ import annotations

import pandas as pd
import streamlit as st


def mostrar_stats_cards(df: pd.DataFrame, indicador: str) -> None:
    """
    Calcula estatísticas descritivas SEM agregação temporal,
    usando a coluna original do indicador.
    """

    if indicador not in df.columns:
        st.error(f"A coluna '{indicador}' não foi encontrada no dataset.")
        return

    # Garante numérico e remove valores inválidos
    s = pd.to_numeric(df[indicador], errors="coerce").dropna()

    if s.empty:
        st.warning("Não há dados numéricos válidos para calcular estatísticas.")
        return

    media = s.mean()
    mediana = s.median()
    desvio = s.std(ddof=1)
    cv = (desvio / media * 100) if media != 0 else float("nan")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Média", f"{media:,.2f}")
    col2.metric("Mediana", f"{mediana:,.2f}")
    col3.metric("Desvio padrão", f"{desvio:,.2f}")
    col4.metric("CV (%)", f"{cv:,.1f}")

    # Se quiser, dá para colocar um comentário rápido:
    if cv < 10:
        st.caption("O indicador é **estável**, com baixa variabilidade (CV < 10%).")
    elif cv < 20:
        st.caption("O indicador tem **variabilidade moderada** (10% ≤ CV < 20%).")
    else:
        st.caption("O indicador apresenta **alta variabilidade** (CV ≥ 20%).")

