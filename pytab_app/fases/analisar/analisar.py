import pandas as pd
import streamlit as st

from pytab.charts.theme import apply_pytab_theme
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


def fase_analisar(df: pd.DataFrame) -> None:
    st.header("Fase Analisar — Identificação de causas")

    abas = st.tabs(
        [
            "Correlação",
            "Pareto",
            "Regressão",
            "Testes estatísticos",
            "Narrativa automática",
        ]
    )

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # ============================================================
    # ABA 1 — CORRELAÇÃO
    # ============================================================
    with abas[0]:
        try:
            mostrar_correlacao_streamlit(df)
        except Exception as e:
            st.error(f"Erro ao calcular correlações: {e}")

    # ============================================================
    # ABA 2 — PARETO
    # ============================================================
    with abas[1]:
        try:
            analisar_pareto(df)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de Pareto: {e}")

    # ============================================================
    # ABA 3 — REGRESSÃO
    # ============================================================
    with abas[2]:
        try:
            analisar_regressao(df)
        except Exception as e:
            st.error(f"Erro ao executar regressão: {e}")

    # ============================================================
    # ABA 4 — TESTES ESTATÍSTICOS
    # ============================================================
    with abas[3]:
        st.subheader("Testes Estatísticos")

        tipo = st.selectbox(
            "Selecione o tipo de teste",
            [
                "Teste t — 1 amostra",
                "Teste t — 2 amostras",
                "Teste t — Pareado",
                "ANOVA One-Way",
                "Qui-Quadrado",
                "Normalidade",
            ],
        )

        # ---------------------- TESTE t 1 AMOSTRA ----------------------
        if tipo == "Teste t — 1 amostra":
            if not num_cols:
                st.warning("Não há colunas numéricas para este teste.")
            else:
                col = st.selectbox("Variável numérica", num_cols)

                s = df[col].dropna()
                if s.empty:
                    st.warning("A coluna selecionada não possui valores numéricos válidos.")
                else:
                    mean_obs = float(s.mean())

                    st.caption(
                        "Informe a média hipotética (μ₀) — normalmente uma meta, especificação ou baseline externo."
                    )

                    mu0 = st.number_input(
                        "Média hipotética (μ₀)",
                        value=round(mean_obs, 2),
                        step=0.1,
                        format="%.2f",
                    )

                    # Guardrail: evita teste trivial sem querer
                    if abs(mu0 - mean_obs) < 1e-9:
                        st.warning(
                            "μ₀ está igual à média observada. Isso torna o teste trivial (t≈0, p≈1). "
                            "Altere μ₀ para uma meta/especificação, ou confirme explicitamente se quiser esse cenário."
                        )
                        confirmar = st.checkbox(
                            "Confirmo que quero testar com μ₀ igual à média observada",
                            value=False,
                        )
                        if not confirmar:
                            st.stop()

                    res = teste_t_uma_amostra(df[col], mu0)
                    st.markdown(narrativa_t(res, "1-amostra"))

        # ---------------------- TESTE t 2 AMOSTRAS ----------------------
        elif tipo == "Teste t — 2 amostras":
            if not num_cols or not cat_cols:
                st.warning("É necessário ter ao menos uma variável numérica e uma categórica.")
            else:
                numcol = st.selectbox("Variável numérica", num_cols)
                cat = st.selectbox("Variável categórica (grupos)", cat_cols)

                grupos = df[cat].dropna().unique()
                if len(grupos) < 2:
                    st.warning("A variável categórica selecionada precisa ter pelo menos 2 grupos.")
                else:
                    g1_label = st.selectbox("Grupo 1", grupos, index=0, key="t2_g1")
                    g2_opcoes = [g for g in grupos if g != g1_label]
                    if not g2_opcoes:
                        st.warning("Selecione uma variável com mais de 1 grupo distinto.")
                    else:
                        g2_label = st.selectbox("Grupo 2", g2_opcoes, index=0, key="t2_g2")

                        g1 = df[df[cat] == g1_label][numcol]
                        g2 = df[df[cat] == g2_label][numcol]

                        res = teste_t_duas_amostras(g1, g2)
                        st.markdown(narrativa_t(res, "2-amostras"))

        # ---------------------- TESTE t PAREADO ----------------------
        elif tipo == "Teste t — Pareado":
            if len(num_cols) < 2:
                st.warning("São necessárias pelo menos duas variáveis numéricas.")
            else:
                col1 = st.selectbox("Primeira variável", num_cols, index=0)
                col2 = st.selectbox(
                    "Segunda variável",
                    [c for c in num_cols if c != col1],
                    index=0,
                )

                res = teste_t_pareado(df[col1], df[col2])
                st.markdown(narrativa_t(res, "pareado"))

        # ---------------------- ANOVA ----------------------
        elif tipo == "ANOVA One-Way":
            if not num_cols or not cat_cols:
                st.warning("É necessário ter ao menos uma variável numérica e uma categórica.")
            else:
                numcol = st.selectbox("Variável numérica", num_cols)
                cat = st.selectbox("Variável categórica (fatores)", cat_cols)

                try:
                    res = anova_oneway(df, numcol, cat)
                    if "anova" in res:
                        st.write(res["anova"])
                    elif "anova_table" in res:
                        st.write(res["anova_table"])
                    st.markdown(narrativa_anova(res))
                except Exception as e:
                    st.error(f"Erro ao executar ANOVA: {e}")

        # ---------------------- QUI-QUADRADO ----------------------
        elif tipo == "Qui-Quadrado":
            if len(cat_cols) < 2:
                st.warning("São necessárias pelo menos duas variáveis categóricas.")
            else:
                c1 = st.selectbox("Variável categórica 1", cat_cols)
                c2 = st.selectbox("Variável categórica 2", [c for c in cat_cols if c != c1])

                res = teste_quiquadrado(df, c1, c2)
                if "tabela" in res:
                    st.write(res["tabela"])
                elif "table" in res:
                    st.write(res["table"])
                st.markdown(narrativa_quiquadrado(res))

        # ---------------------- NORMALIDADE ----------------------
        elif tipo == "Normalidade":
            if not num_cols:
                st.warning("Não há colunas numéricas para testar normalidade.")
            else:
                col = st.selectbox("Variável numérica", num_cols)
                res = teste_normalidade(df[col])
                st.markdown(narrativa_normalidade(res))
                fig = qqplot_figure(df[col])
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # ABA 5 — NARRATIVA AUTOMÁTICA (CONSOLIDADA)
    # ============================================================
    with abas[4]:
        st.subheader("Narrativa automática consolidada (em desenvolvimento)")
        st.info(
            "Aqui o PyTab vai integrar os principais achados de Correlação, Pareto, "
            "Regressão e Testes estatísticos em uma narrativa única para o projeto DMAIC."
        )
