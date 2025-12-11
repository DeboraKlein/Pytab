import streamlit as st
import pandas as pd

from pytab.charts.theme import apply_pytab_theme

# Submódulos
from pytab_app.fases.analisar.correlacao import mostrar_correlacao_streamlit
from pytab_app.fases.analisar.pareto import analisar_pareto
from pytab_app.fases.analisar.regressao import analisar_regressao
from pytab_app.modules.testes_estatisticos import (
    teste_t_uma_amostra,
    teste_t_duas_amostras,
    teste_t_pareado,
    narrativa_t,
    anova_oneway,
    narrativa_anova,
    teste_quiquadrado,
    narrativa_quiquadrado,
    teste_normalidade,
    qqplot_figure,
    narrativa_normalidade,
)

apply_pytab_theme()


def fase_analisar(df: pd.DataFrame):
    st.header("Fase Analisar — Identificação de Causas")

    tabs = st.tabs([
        "Correlação entre variáveis",
        "Análise de Pareto",
        "Regressão Linear",
        "Testes estatísticos",
        "Narrativa automática",
    ])

    # ============================================================
    # TAB 1 — CORRELAÇÃO
    # ============================================================
    with tabs[0]:
        st.subheader("Correlação entre variáveis")
        try:
            mostrar_correlacao_streamlit(df)
        except Exception as e:
            st.error(f"Erro ao calcular correlações: {e}")

    # ============================================================
    # TAB 2 — PARETO
    # ============================================================
    with tabs[1]:
        st.subheader("Análise de Pareto")
        try:
            fig_pareto, tabela_pareto = analisar_pareto(df)

            if fig_pareto is not None:
                st.pyplot(fig_pareto)

            if tabela_pareto is not None:
                st.markdown("### Tabela de Contribuições")
                st.dataframe(tabela_pareto)

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de Pareto: {e}")

    # ============================================================
    # TAB 3 — REGRESSÃO
    # ============================================================
    with tabs[2]:
        st.subheader("Regressão Linear Simples")

        try:
            resultado = analisar_regressao(df)

            if isinstance(resultado, list):
                for bloco in resultado:
                    st.markdown(bloco)
            else:
                st.markdown(resultado)

        except Exception as e:
            st.error(f"Erro ao executar regressão: {e}")

    # ============================================================
    # TAB 4 — TESTES ESTATÍSTICOS
    # ============================================================
    with tabs[3]:
        st.subheader("Testes Estatísticos")

        cols = df.columns.tolist()

        tipo = st.selectbox(
            "Tipo de teste",
            [
                "Teste t — 1 amostra",
                "Teste t — 2 amostras",
                "Teste t — Pareado",
                "ANOVA One-Way",
                "Qui-Quadrado",
                "Normalidade",
            ],
        )

        # --- 1 Amostra ---
        if tipo == "Teste t — 1 amostra":
            numcol = st.selectbox("Variável numérica", df.select_dtypes(include=["number"]).columns)
            media_hip = st.number_input("Média hipotética", value=0.0)
            res = teste_t_uma_amostra(df[numcol], media_hip)
            st.markdown(narrativa_t(res, "1-amostra"))

        # --- 2 Amostras ---
        elif tipo == "Teste t — 2 amostras":
            numcol = st.selectbox("Variável numérica", df.select_dtypes(include=["number"]).columns)
            cat = st.selectbox("Variável categórica", df.select_dtypes(include=["object", "category"]).columns)

            grupos = df[cat].dropna().unique()
            if len(grupos) != 2:
                st.warning("A variável categórica deve ter exatamente 2 grupos.")
            else:
                g1 = df[df[cat] == grupos[0]][numcol]
                g2 = df[df[cat] == grupos[1]][numcol]
                res = teste_t_duas_amostras(g1, g2)
                st.markdown(narrativa_t(res, "2-amostras"))

        # --- Pareado ---
        elif tipo == "Teste t — Pareado":
            cols_num = df.select_dtypes(include=["number"]).columns
            col1 = st.selectbox("Primeira variável", cols_num)
            col2 = st.selectbox("Segunda variável", cols_num)
            res = teste_t_pareado(df[col1], df[col2])
            st.markdown(narrativa_t(res, "pareado"))

        # --- ANOVA ---
        elif tipo == "ANOVA One-Way":
            numcol = st.selectbox("Variável numérica", df.select_dtypes(include=["number"]).columns)
            cat = st.selectbox("Variável categórica", df.select_dtypes(include=["object", "category"]).columns)
            res = anova_oneway(df, numcol, cat)
            st.write(res["anova"])
            st.markdown(narrativa_anova(res))

        # --- Qui-Quadrado ---
        elif tipo == "Qui-Quadrado":
            c1 = st.selectbox("Variável categórica 1", df.select_dtypes(include=["object", "category"]).columns)
            c2 = st.selectbox("Variável categórica 2", df.select_dtypes(include=["object", "category"]).columns)
            res = teste_quiquadrado(df, c1, c2)
            st.write(res["tabela"])
            st.markdown(narrativa_quiquadrado(res))

        # --- Normalidade ---
        elif tipo == "Normalidade":
            col = st.selectbox("Variável numérica", df.select_dtypes(include=["number"]).columns)
            res = teste_normalidade(df[col])
            st.markdown(narrativa_normalidade(res))
            fig = qqplot_figure(df[col])
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5 — NARRATIVA AUTOMÁTICA FUTURA
    # ============================================================
    with tabs[4]:
        st.subheader("Narrativa automática consolidada")
        st.info("Em desenvolvimento: será uma narrativa única integrando Pareto + Correlação + Regressão.")
