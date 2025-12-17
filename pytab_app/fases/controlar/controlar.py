import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pytab.charts.theme import apply_pytab_theme
from .charts import carta_imr, carta_xbar_r, carta_p, carta_u
from .narrativa import narrativa_imr, narrativa_xbar_r, narrativa_p, narrativa_u

apply_pytab_theme()


def _colunas_numericas(df: pd.DataFrame):
    return df.select_dtypes(include=["number"]).columns.tolist()


def _colunas_categoricas(df: pd.DataFrame):
    return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


def _detectar_tipo_default(df: pd.DataFrame) -> str:
    """
    Heurística simples para sugerir tipo de carta quando 'Automático' é escolhido.
    - Se houver coluna 'defeituosos' + 'inspecionados' → P-Chart
    - Se houver 'defeitos' + 'oportunidades' → U-Chart
    - Caso contrário → I-MR
    """
    cols = [c.lower() for c in df.columns]

    if ("defeituosos" in cols or "defeituosos_qtd" in cols) and (
        "inspecionados" in cols or "inspecionados_qtd" in cols
    ):
        return "P-Chart (Proporção defeituosos)"

    if ("defeitos" in cols or "defeitos_qtd" in cols) and (
        "oportunidades" in cols or "oportunidades_qtd" in cols
    ):
        return "U-Chart (Defeitos por unidade)"

    # Default seguro
    return "I-MR (Individuais)"


def fase_controlar(df: pd.DataFrame) -> None:
    st.header("Fase Controlar — Acompanhar o Processo ao Longo do Tempo")

    opcoes = [
        "Automático (recomendado)",
        "I-MR (Individuais)",
        "X̄-R (Subgrupos)",
        "P-Chart (Proporção defeituosos)",
        "U-Chart (Defeitos por unidade)",
    ]

    tipo_carta = st.selectbox("Tipo de carta de controle", opcoes)

    # Se o usuário escolheu automático, definimos a sugestão
    if tipo_carta == "Automático (recomendado)":
        sugestao = _detectar_tipo_default(df)
        st.info(f"Sugestão automática baseada na estrutura dos dados: **{sugestao}**")
        tipo_carta = sugestao

    num_cols = _colunas_numericas(df)

    # ------------------------------------------------------------------
    # I-MR e X̄-R
    # ------------------------------------------------------------------
    if tipo_carta in ["I-MR (Individuais)", "X̄-R (Subgrupos)"]:
        if not num_cols:
            st.warning("Nenhuma coluna numérica disponível para cartas de controle contínuas.")
            return

        indicador = st.selectbox("Selecione o indicador numérico", num_cols)

        if tipo_carta == "I-MR (Individuais)":
            try:
                fig, resumo = carta_imr(df[indicador])
                st.pyplot(fig)
                plt.close(fig)
                st.markdown(narrativa_imr(indicador, resumo))
            except Exception as e:
                st.error(f"Erro ao gerar carta I-MR: {e}")

        else:  # X̄-R
            n_sub = st.number_input(
                "Tamanho do subgrupo (2 a 6)",
                min_value=2,
                max_value=6,
                value=5,
                step=1,
            )
            try:
                fig, resumo = carta_xbar_r(df[indicador], int(n_sub))
                st.pyplot(fig)
                plt.close(fig)
                st.markdown(narrativa_xbar_r(indicador, resumo))
            except Exception as e:
                st.error(f"Erro ao gerar carta X̄-R: {e}")

        return

    # ------------------------------------------------------------------
    # P-CHART
    # ------------------------------------------------------------------
    if tipo_carta == "P-Chart (Proporção defeituosos)":
        if len(num_cols) < 2:
            st.warning("São necessárias pelo menos 2 colunas numéricas (defeituosos e inspecionados).")
            return

        col_def = st.selectbox("Número de defeituosos", num_cols, key="p_def")
        tot_opcoes = [c for c in num_cols if c != col_def]
        if not tot_opcoes:
            st.warning("Selecione um arquivo com pelo menos duas colunas numéricas distintas.")
            return

        col_tot = st.selectbox("Total inspecionado", tot_opcoes, key="p_tot")

        try:
            fig, resumo = carta_p(df[col_def], df[col_tot])
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_p(col_def, col_tot, resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta P: {repr(e)}")

        return

    # ------------------------------------------------------------------
    # U-CHART
    # ------------------------------------------------------------------
    if tipo_carta == "U-Chart (Defeitos por unidade)":
        if len(num_cols) < 2:
            st.warning("São necessárias pelo menos 2 colunas numéricas (defeitos e oportunidades).")
            return

        col_def = st.selectbox("Número de defeitos", num_cols, key="u_def")
        opp_opcoes = [c for c in num_cols if c != col_def]
        if not opp_opcoes:
            st.warning("Selecione um arquivo com pelo menos duas colunas numéricas distintas.")
            return

        col_opp = st.selectbox("Unidades de oportunidade", opp_opcoes, key="u_opp")

        try:
            fig, resumo = carta_u(df[col_def], df[col_opp])
            st.pyplot(fig)
            plt.close(fig)
            st.markdown(narrativa_u(col_def, col_opp, resumo))
        except Exception as e:
            st.error(f"Erro ao gerar carta U: {repr(e)}")

        return

