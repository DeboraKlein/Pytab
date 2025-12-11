import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pytab.charts.theme import apply_pytab_theme
from .charts import carta_imr, carta_xbar_r, carta_p, carta_u
from .narrativa import narrativa_imr, narrativa_xbar_r, narrativa_p, narrativa_u

apply_pytab_theme()


def fase_controlar(df: pd.DataFrame) -> None:
    st.header("Fase Controlar — Acompanhar o Processo ao Longo do Tempo")

    tipo_carta = st.selectbox(
        "Tipo de carta de controle",
        [
            "Automático (recomendado)",
            "I-MR (Individuais)",
            "X̄-R (Subgrupos)",
            "P-Chart (Proporção defeituosos)",
            "U-Chart (Defeitos por unidade)",
        ],
    )

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if tipo_carta in ["Automático (recomendado)", "I-MR (Individuais)", "X̄-R (Subgrupos)"]:
        if not num_cols:
            st.warning("Nenhuma coluna numérica disponível para cartas I-MR/X̄-R.")
            return

        indicador = st.selectbox("Selecione o indicador numérico", num_cols)

    # ------------------------------
    # Automático = I-MR simples por enquanto
    # ------------------------------
    if tipo_carta == "Automático (recomendado)":
        st.info("Modo automático: utilizando Carta I-MR para dados individuais.")
        try:
            fig, resumo = carta_imr(df[indicador])
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_imr(resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta I-MR: {e}")

    # ------------------------------
    # I-MR
    # ------------------------------
    elif tipo_carta == "I-MR (Individuais)":
        try:
            fig, resumo = carta_imr(df[indicador])
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_imr(resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta I-MR: {e}")

    # ------------------------------
    # XBAR-R
    # ------------------------------
    elif tipo_carta == "X̄-R (Subgrupos)":
        n_sub = st.number_input("Tamanho do subgrupo", min_value=2, max_value=6, value=5, step=1)
        try:
            fig, resumo = carta_xbar_r(df[indicador], int(n_sub))
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_xbar_r(resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta X̄-R: {e}")

    # ------------------------------
    # P-CHART
    # ------------------------------
    elif tipo_carta == "P-Chart (Proporção defeituosos)":
        st.info("Informe colunas de número de itens defeituosos e total inspecionado em cada amostra.")

        if not num_cols:
            st.warning("Não há colunas numéricas suficientes para carta P.")
            return

        col_def = st.selectbox("Itens defeituosos", num_cols)
        col_tot = st.selectbox("Total inspecionado", [c for c in num_cols if c != col_def])

        try:
            fig, resumo = carta_p(df[col_def], df[col_tot])
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_p(resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta P: {e}")

    # ------------------------------
    # U-CHART
    # ------------------------------
    elif tipo_carta == "U-Chart (Defeitos por unidade)":
        st.info("Informe colunas de número de defeitos e unidades de oportunidade em cada amostra.")

        if not num_cols:
            st.warning("Não há colunas numéricas suficientes para carta U.")
            return

        col_def = st.selectbox("Número de defeitos", num_cols)
        col_opp = st.selectbox("Unidades de oportunidade", [c for c in num_cols if c != col_def])

        try:
            fig, resumo = carta_u(df[col_def], df[col_opp])
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_u(resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta U: {e}")
