import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pytab.charts.theme import apply_pytab_theme

from .otimizacao import calcular_gap, simular_cenarios
from .antes_depois import analisar_antes_depois
from .variacao import calcular_variacao, grafico_variacao
from .causas_solucoes import matriz_impacto_esforco

apply_pytab_theme()


def _detect_date_cols(df: pd.DataFrame) -> list[str]:
    """Detecta colunas datetime e também colunas object que parecem data."""
    dt_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]", "datetimetz"]).columns.tolist()
    if dt_cols:
        return dt_cols

    obj_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    good = []
    for c in obj_cols:
        parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
        if parsed.notna().mean() >= 0.6:
            good.append(c)
    return good


def fase_melhorar(df: pd.DataFrame):
    st.header("Fase Melhorar — Testar Soluções e Otimizar o Processo")

    aba1, aba2, aba3, aba4 = st.tabs(
        ["Otimização e Meta", "Redução de Variação", "Antes / Depois", "Causas vs Soluções"]
    )

    # Define UMA vez e reutiliza (evita NameError)
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    # ============================================================
    # 1) OTIMIZAÇÃO
    # ============================================================
    with aba1:
        st.subheader("Otimização simples — Meta, Gap e Cenários")

        if not num_cols:
            st.warning("Nenhuma coluna numérica disponível para a fase Melhorar.")
            st.stop()

        indicador = st.selectbox("Selecione o indicador", num_cols, key="melhorar_indicador_aba1")

        meta = st.number_input(
            "Meta desejada",
            value=float(df[indicador].dropna().mean()) if df[indicador].dropna().size else 0.0,
        )

        atual, gap = calcular_gap(df[indicador], meta)

        st.metric(label="Gap atual", value=f"{gap:.2f}", delta=f"{meta - atual:.2f}")

        st.markdown("### Simulação de cenários")

        melhoria_pct = st.slider("Redução esperada (%)", 0.0, 80.0, 10.0)
        resultado = simular_cenarios(df[indicador], melhoria_pct)

        st.write("Resultados simulados:")
        st.dataframe(resultado)

    # ============================================================
    # 2) REDUÇÃO DE VARIAÇÃO
    # ============================================================
    with aba2:
        st.subheader("Redução de Variação")

        if not num_cols:
            st.warning("Nenhuma coluna numérica disponível para esta análise.")
            st.stop()

        indicador = st.selectbox("Selecione indicador numérico", num_cols, key="melhorar_indicador_aba2")

        antes, depois, resumo = calcular_variacao(df[indicador])
        fig = grafico_variacao(antes, depois)

        st.pyplot(fig)
        plt.close(fig)

        st.markdown("### Interpretação")
        st.write(resumo)

    # ============================================================
    # 3) ANTES / DEPOIS
    # ============================================================
    with aba3:
        st.subheader("Comparação Antes / Depois de uma mudança")

        if not num_cols:
            st.warning("Nenhuma coluna numérica disponível para esta análise.")
            st.stop()

        data_cols = _detect_date_cols(df)
        if not data_cols:
            st.warning("Nenhuma coluna de data encontrada para realizar análise antes/depois.")
        else:
            data_col = st.selectbox("Coluna de data", data_cols, key="melhorar_data_col")

            data_cut = st.date_input("Data da mudança")

            col_num = st.selectbox("Indicador para comparar", num_cols, key="melhorar_indicador_aba3")

            res, fig = analisar_antes_depois(df, data_col, col_num, data_cut)

            st.pyplot(fig)
            plt.close(fig)

            st.markdown("### Resultados")
            st.dataframe(res)

    # ============================================================
    # 4) CAUSAS / SOLUÇÕES
    # ============================================================
    with aba4:
        st.subheader("Matriz Impacto x Esforço")

        st.markdown(
            """
        Classifique cada solução candidata com notas de **1 a 5**.
        O PyTab recomenda automaticamente quais priorizar.
        """
        )

        soluções = st.text_area(
            "Liste as soluções (uma por linha)",
            placeholder="Treinamento da equipe\nAutomação parcial\nMelhoria do layout",
        ).split("\n")

        solucoes_limpas = [s.strip() for s in soluções if s.strip()]

        if solucoes_limpas:
            df_mat = matriz_impacto_esforco(solucoes_limpas)
            st.dataframe(df_mat)

            st.subheader("Recomendação PyTab")
            melhores = df_mat.sort_values("Prioridade", ascending=False).head(3)
            st.write(melhores)
        else:
            st.info("Insira pelo menos uma solução.")
