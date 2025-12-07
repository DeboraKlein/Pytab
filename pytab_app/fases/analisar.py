import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def fase_analisar(df: pd.DataFrame, types: dict) -> None:
    st.markdown("## Fase A — Analisar")
    st.write(
        """
Nesta fase, o objetivo é entender **por que** o processo se comporta da forma observada.

O PyTab ajuda você a:
- explorar relações entre variáveis numéricas (correlação),
- visualizar a relação entre duas variáveis (dispersão),
- identificar categorias que mais contribuem para um resultado (Pareto simples).
"""
    )

    numeric_cols = types.get("numeric", [])
    categorical_cols = types.get("categorical", [])

    # 1. Correlação entre variáveis numéricas
    st.markdown("### 1. Correlação entre variáveis numéricas")

    if len(numeric_cols) < 2:
        st.info(
            "São necessárias pelo menos duas colunas numéricas para análise de correlação."
        )
    else:
        df_num = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        df_num = df_num.dropna(how="all")

        if df_num.empty:
            st.info("Os dados numéricos não são suficientes para calcular correlações.")
        else:
            corr = df_num.corr()

            st.write("**Matriz de correlação (Pearson)**")
            st.dataframe(corr.style.format("{:.2f}"))

            alvo = st.selectbox(
                "Selecione um indicador para ver quais variáveis se relacionam mais com ele:",
                options=numeric_cols,
            )

            if alvo in corr.columns:
                corr_alvo = corr[alvo].drop(labels=[alvo]).dropna()
                if corr_alvo.empty:
                    st.info(
                        "Não foi possível calcular correlações relevantes para o indicador selecionado."
                    )
                else:
                    corr_ord = corr_alvo.reindex(
                        corr_alvo.abs().sort_values(ascending=False).index
                    )
                    st.markdown("**Relações com o indicador selecionado**")
                    st.dataframe(
                        corr_ord.to_frame(name="correlação").style.format("{:.2f}")
                    )

                    top_var = corr_ord.index[0]
                    top_val = corr_ord.iloc[0]
                    st.write(
                        f"A variável com maior correlação com **{alvo}** é **{top_var}** "
                        f"(correlação de aproximadamente {top_val:.2f})."
                    )

                    st.markdown("#### Visualização da relação mais forte (dispersão)")
                    x = df_num[top_var]
                    y = df_num[alvo]
                    mask = x.notna() & y.notna()
                    x = x[mask]
                    y = y[mask]

                    if x.empty or y.empty:
                        st.info("Não há dados suficientes para o gráfico de dispersão.")
                    else:
                        fig, ax = plt.subplots()
                        ax.scatter(x, y)
                        ax.set_xlabel(top_var)
                        ax.set_ylabel(alvo)

                        try:
                            coef = np.polyfit(x, y, 1)
                            x_line = np.linspace(x.min(), x.max(), 50)
                            y_line = coef[0] * x_line + coef[1]
                            ax.plot(x_line, y_line, label="Tendência linear")
                            ax.legend()
                        except Exception:
                            pass

                        st.pyplot(fig)

                        st.caption(
                            "Este gráfico ajuda a visualizar se aumentos em uma variável "
                            "estão associados a aumentos ou reduções na outra."
                        )

    st.markdown("---")

    # 2. Pareto simples para categorias
    st.markdown("### 2. Pareto simples (frequência por categoria)")

    if not categorical_cols:
        st.info(
            "Não foram identificadas colunas categóricas no conjunto de dados. "
            "Colunas de texto ou códigos costumam ser interpretadas como categóricas."
        )
    else:
        cat_col = st.selectbox(
            "Selecione uma coluna categórica para análise de Pareto:",
            options=categorical_cols,
        )

        serie_cat = df[cat_col].astype("string")
        counts = serie_cat.value_counts(dropna=True)

        if counts.empty:
            st.info("Não há dados suficientes para análise de Pareto nesta coluna.")
        else:
            total = counts.sum()
            cum_pct = counts.cumsum() / total * 100
            pareto_df = pd.DataFrame(
                {"frequência": counts, "acumulado_%": cum_pct}
            )

            st.markdown("**Tabela de Pareto (frequência e percentual acumulado)**")
            st.dataframe(pareto_df)

            x_labels = pareto_df.index.astype(str)

            fig_p, ax_p = plt.subplots()
            ax_p.bar(x_labels, pareto_df["frequência"], zorder=1)
            ax_p.set_xlabel(cat_col)
            ax_p.set_ylabel("Frequência")
            ax_p.tick_params(axis="x", rotation=45)

            ax2 = ax_p.twinx()
            ax2.plot(
                x_labels,
                pareto_df["acumulado_%"],
                marker="o",
                linestyle="-",
                linewidth=2,
                zorder=5,
            )
            ax2.set_ylabel("% acumulado")
            ax2.set_ylim(0, 110)

            st.pyplot(fig_p)

            top_n = min(3, len(pareto_df))
            principais = pareto_df.head(top_n)
            pct_top = principais["acumulado_%"].iloc[-1]

            st.write(
                f"As **{top_n}** categorias mais frequentes representam aproximadamente "
                f"**{pct_top:.1f}%** de todas as ocorrências. "
                "Essas categorias costumam ser um bom ponto de partida para priorização."
            )
