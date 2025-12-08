import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from pytab.stats.descriptive import summarize_numeric
from pytab.stats.outliers import detect_outliers


def _classify_cv(cv: float) -> str:
    if pd.isna(cv):
        return "não foi possível avaliar a variabilidade."
    if cv < 10:
        return "variação baixa (processo bastante estável)."
    if cv < 20:
        return "variação moderada (processo relativamente estável)."
    if cv < 30:
        return "variação considerável (atenção à variabilidade)."
    return "variação alta (processo instável, recomenda-se investigação)."


def _build_indicator_summary(series: pd.Series, summary_row: pd.Series) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return "Não há dados numéricos suficientes para gerar um resumo interpretativo."

    minimum = summary_row.get("min", s.min())
    q1 = summary_row.get("q1", s.quantile(0.25))
    median = summary_row.get("median", s.median())
    q3 = summary_row.get("q3", s.quantile(0.75))
    maximum = summary_row.get("max", s.max())
    mean = summary_row.get("mean", s.mean())
    cv = summary_row.get("cv", float("nan"))

    texto = []
    texto.append(
        f"O indicador apresenta valores entre aproximadamente {minimum:.2f} e {maximum:.2f}, "
        f"com mediana em torno de {median:.2f}."
    )
    texto.append(
        f"Os valores típicos (entre o primeiro e o terceiro quartil) vão de {q1:.2f} a {q3:.2f}."
    )
    texto.append(
        f"A média observada é de {mean:.2f}, e o coeficiente de variação indica "
        f"{_classify_cv(cv)}"
    )

    return " ".join(texto)


def _suggest_time_freq(n_points: int) -> str:
    """
    Sugere frequência de agregação com base em quantidade de DIAS distintos.
    """
    if n_points <= 120:
        return "D"
    if n_points <= 365:
        return "W"
    if n_points <= 5 * 365:
        return "M"
    if n_points <= 15 * 365:
        return "Q"
    return "A"


def _freq_options():
    return {
        "Diária": "D",
        "Semanal": "W",
        "Mensal": "M",
        "Trimestral": "Q",
        "Anual": "A",
    }


def _freq_label(freq: str) -> str:
    return {
        "D": "Diária",
        "W": "Semanal",
        "M": "Mensal",
        "Q": "Trimestral",
        "A": "Anual",
    }.get(freq, "Diária")


def _default_rolling_window(freq_code: str) -> int:
    if freq_code == "D":
        return 7
    if freq_code == "W":
        return 4
    if freq_code == "M":
        return 3
    if freq_code == "Q":
        return 2
    if freq_code == "A":
        return 2
    return 3


def fase_medir(df: pd.DataFrame, types: dict) -> None:
    st.markdown("## Fase M — Medir")
    st.write(
        """
Aqui avaliamos **como o processo se comporta hoje**:
- nível (média, mediana),
- variabilidade (desvio padrão, coeficiente de variação),
- distribuição (histograma, boxplot),
- comportamento ao longo do tempo,
- valores muito fora do padrão (outliers).
"""
    )

    numeric_cols = types.get("numeric", [])
    datetime_cols = types.get("datetime", [])

    st.markdown("### 1. Escolha do indicador numérico a ser analisado")
    if not numeric_cols:
        st.info(
            "Nenhuma coluna numérica foi identificada. "
            "Verifique se o arquivo contém dados numéricos."
        )
        return

    indicador = st.selectbox(
        "Selecione a coluna numérica que você quer analisar em detalhe:",
        options=numeric_cols,
    )

    serie = pd.to_numeric(df[indicador], errors="coerce")
    serie_valid = serie.dropna()

    if serie_valid.empty:
        st.info(
            "A coluna selecionada não possui dados numéricos válidos suficientes para análise."
        )
        return

    # Estatísticas descritivas
    st.markdown("### 2. Estatísticas descritivas e interpretação")

    summary_all = summarize_numeric(df)
    if isinstance(summary_all, pd.DataFrame) and indicador in summary_all.index:
        row = summary_all.loc[indicador]
    else:
        row = pd.Series(
            {
                "count": serie_valid.count(),
                "mean": serie_valid.mean(),
                "median": serie_valid.median(),
                "std": serie_valid.std(),
                "min": serie_valid.min(),
                "q1": serie_valid.quantile(0.25),
                "q3": serie_valid.quantile(0.75),
                "max": serie_valid.max(),
                "cv": (serie_valid.std() / serie_valid.mean() * 100)
                if serie_valid.mean() != 0
                else float("nan"),
            }
        )

    cv_value = float(row.get("cv", np.nan))

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Valores válidos", int(row.get("count", len(serie_valid))))
    with k2:
        st.metric("Média", f"{row.get('mean', serie_valid.mean()):.2f}")
    with k3:
        st.metric("Mediana", f"{row.get('median', serie_valid.median()):.2f}")
    with k4:
        st.metric("Desvio padrão", f"{row.get('std', serie_valid.std()):.2f}")
    with k5:
        if not pd.isna(cv_value):
            st.metric("Coef. variação (CV)", f"{cv_value:.1f}%")
        else:
            st.metric("Coef. variação (CV)", "n/d")

    st.caption("Classificação da variabilidade: " + _classify_cv(cv_value))

    texto_resumo = _build_indicator_summary(serie_valid, row)
    st.markdown("**Resumo interpretativo do indicador**")
    st.write(texto_resumo)

    # Distribuição
    st.markdown("### 3. Distribuição do indicador")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.write("**Distribuição (histograma)**")
        fig, ax = plt.subplots()
        ax.hist(serie_valid, bins="auto")
        ax.set_xlabel(indicador)
        ax.set_ylabel("Frequência")
        st.pyplot(fig)

    with col_g2:
        st.write("**Dispersão e possíveis outliers (boxplot)**")
        fig2, ax2 = plt.subplots()
        ax2.boxplot(serie_valid, vert=True, showfliers=True)
        ax2.set_xlabel(indicador)
        st.pyplot(fig2)

    # Série temporal agregada + média móvel
    if datetime_cols:
        st.markdown("### 4. Evolução do indicador ao longo do tempo")

        col_dt1, col_dt2 = st.columns([2, 3])
        with col_dt1:
            data_col = st.selectbox(
                "Selecione a coluna de data/tempo associada ao indicador:",
                options=datetime_cols,
            )
        with col_dt2:
            st.write(
                "Abaixo é apresentada uma visão agregada do indicador ao longo do tempo, "
                "com possibilidade de ajustar o nível de agregação e a média móvel."
            )

        df_time = df[[data_col, indicador]].copy()
        df_time[data_col] = pd.to_datetime(df_time[data_col], errors="coerce")
        df_time = df_time.dropna(subset=[data_col])
        df_time = df_time.sort_values(data_col)

        if not df_time.empty:
            n_days = df_time[data_col].dt.date.nunique()
            suggested_freq = _suggest_time_freq(n_days)
            freq_map = _freq_options()

            st.write(
                f"Foram encontrados **{n_days}** dias distintos na série temporal. "
                f"Sugestão automática de agregação: **{_freq_label(suggested_freq)}**."
            )

            freq_label = st.selectbox(
                "Nível de agregação desejado:",
                options=list(freq_map.keys()),
                index=list(freq_map.values()).index(suggested_freq),
            )
            freq_code = freq_map[freq_label]

            ts_agg = (
                df_time.set_index(data_col)[indicador]
                .resample(freq_code)
                .mean()
                .dropna()
            )

            if ts_agg.empty:
                st.info(
                    "Não foi possível gerar série temporal agregada com os dados atuais."
                )
            else:
                default_window = _default_rolling_window(freq_code)
                max_window = max(2, min(12, len(ts_agg)))
                window = st.slider(
                    "Janela da média móvel (em número de períodos agregados):",
                    min_value=1,
                    max_value=max_window,
                    value=min(default_window, max_window),
                )

                ts_ma = ts_agg.rolling(window=window).mean()

                fig3, ax3 = plt.subplots()
                ax3.plot(ts_agg.index, ts_agg.values, label="Média agregada")
                ax3.plot(ts_ma.index, ts_ma.values, label="Média móvel")
                ax3.set_xlabel("Tempo")
                ax3.set_ylabel(indicador)
                ax3.legend()
                st.pyplot(fig3)

                mean_ts = ts_agg.mean()
                std_ts = ts_agg.std()
                if std_ts > 0:
                    upper = mean_ts + 3 * std_ts
                    lower = mean_ts - 3 * std_ts
                    st.write(
                        f"Limites naturais aproximados do processo (média ± 3 desvios) "
                        f"na série agregada: de **{lower:.2f}** a **{upper:.2f}**."
                    )
                st.caption(
                    f"A série foi agregada em nível **{freq_label.lower()}** "
                    f"e suavizada com média móvel de **{window}** período(s)."
                )
        else:
            st.info(
                "Não foi possível gerar a série temporal com os dados atuais "
                "(datas inválidas ou ausentes)."
            )

    # Outliers
    st.markdown("### 5. Detecção de valores muito fora do padrão (outliers)")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        method = st.selectbox(
            "Método para detecção de outliers:",
            options=["zscore", "iqr"],
            format_func=lambda x: "Z-score" if x == "zscore" else "IQR (quartis)",
        )
    with col_m2:
        if method == "zscore":
            threshold = st.slider(
                "Limite de |z-score| para considerar outlier:",
                min_value=2.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
            )
            result = detect_outliers(
                serie_valid,
                method="zscore",
                threshold=threshold,
            )
        else:
            factor = st.slider(
                "Fator do IQR:",
                min_value=1.0,
                max_value=3.0,
                value=1.5,
                step=0.1,
            )
            result = detect_outliers(
                serie_valid,
                method="iqr",
                factor=factor,
            )

    summary_out = result["summary"]
    n = summary_out["n"]
    n_out = summary_out["n_outliers"]
    pct_out = summary_out["pct_outliers"]

    if n_out > 0:
        st.write(
            f"Foram encontrados **{n_out}** valores muito fora do padrão "
            f"(cerca de **{pct_out:.2f}%** dos {n} valores válidos). "
        )
    else:
        st.write(
            f"Não foram encontrados outliers de acordo com o método selecionado "
            f"para os {n} valores válidos."
        )

    outliers_df = result["outliers"]
    if not outliers_df.empty:
        st.markdown("**Tabela de valores classificados como outliers**")
        st.dataframe(outliers_df)
    else:
        st.info("Nenhum outlier foi detectado com os parâmetros atuais.")

    with st.expander("Ver detalhamento estatístico (para usuários técnicos)"):
        st.markdown("**Resumo estatístico completo da coluna selecionada**")
        if isinstance(summary_all, pd.DataFrame):
            st.dataframe(summary_all.loc[[indicador]])
        else:
            st.write("Resumo em formato simplificado:")
            st.write(row.to_frame(name="valor"))

        st.markdown(
            """
**Coeficiente de Variação (CV)**  
Mede o quanto o indicador varia em relação à média (em %).  
- CV baixo → processo mais estável  
- CV alto → processo mais instável

**Z-score**  
Mede quantos desvios-padrão cada valor está distante da média.  
Valores com |z| muito alto são candidatos a outliers.

**IQR (Intervalo Interquartil)**  
Mede a faixa central dos dados (entre Q1 e Q3).  
Valores muito abaixo de Q1 ou muito acima de Q3 podem ser considerados outliers.
"""
        )