"""
Aplicativo Streamlit do PyTab
Interface para usuários finais, organizada em torno do ciclo DMAIC.
"""

from pathlib import Path
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from pytab.io.reader import read_any
from pytab.stats.descriptive import summarize_numeric
from pytab.stats.outliers import detect_outliers
from pytab.utils.schema import detect_column_types


# -----------------------------
# Utilitários internos
# -----------------------------
def _load_dataframe(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """
    Salva o arquivo enviado em um temp file e delega leitura ao read_any.
    Isso evita problemas de engine/streams com pandas.
    """
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    df = read_any(temp_path)
    return df


def _check_column_names(df: pd.DataFrame) -> dict:
    """
    Faz uma checagem simples dos nomes das colunas:
      - vazios
      - duplicados
    Retorna um dicionário com listas.
    """
    col_names = list(df.columns)
    empty = [c for c in col_names if str(c).strip() == "" or c is None]

    seen = set()
    duplicated = []
    for c in col_names:
        if c in seen and c not in duplicated:
            duplicated.append(c)
        seen.add(c)

    return {"empty": empty, "duplicated": duplicated}


def _classify_cv(cv: float) -> str:
    """
    Classificação simples do Coeficiente de Variação (CV) em faixas qualitativas.
    """
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
    """
    Gera um texto amigável para humanos, usando as estatísticas descritivas.
    summary_row: uma linha do summarize_numeric (para a coluna selecionada).
    """
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
    Sugere uma frequência de agregação temporal com base no número de pontos.
    Retorna um código de frequência do pandas:
      - 'D' (diária)
      - 'W' (semanal)
      - 'M' (mensal)
      - 'Q' (trimestral)
      - 'A' (anual)
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


def _freq_label(freq: str) -> str:
    return {
        "D": "Diária",
        "W": "Semanal",
        "M": "Mensal",
        "Q": "Trimestral",
        "A": "Anual",
    }.get(freq, "Diária")


def _freq_options():
    return {
        "Diária": "D",
        "Semanal": "W",
        "Mensal": "M",
        "Trimestral": "Q",
        "Anual": "A",
    }


def _default_rolling_window(freq_code: str) -> int:
    """
    Define um tamanho padrão de janela de média móvel dado o nível de agregação.
    """
    if freq_code == "D":
        return 7  # ~1 semana
    if freq_code == "W":
        return 4  # ~1 mês
    if freq_code == "M":
        return 3  # ~1 trimestre
    if freq_code == "Q":
        return 2  # ~meio ano
    if freq_code == "A":
        return 2  # ~2 anos, se fizer sentido
    return 3


# -----------------------------
# Blocos de interface por fase DMAIC
# -----------------------------
def _fase_definir() -> None:
    st.markdown("## Fase D — Definir")
    st.write(
        """
Nesta fase, o foco é esclarecer:
- qual é o problema,
- qual indicador será acompanhado,
- qual o objetivo de melhoria e
- qual o escopo do projeto.

O PyTab entra principalmente a partir da fase **Medir**, mas você pode usar:
- a pré-visualização dos dados,
- as estatísticas básicas e
- a linha do tempo do indicador

para apoiar a construção do *baseline* do problema.
"""
    )


def _fase_medir(df: pd.DataFrame, types: dict) -> None:
    st.markdown("## Fase M — Medir")
    st.write(
        """
Aqui avaliamos **como o processo se comporta hoje**:
- nível (média, mediana),
- variabilidade (desvio padrão, coeficiente de variação),
- distribuição (histograma, boxplot),
- valores muito fora do padrão (outliers),
- comportamento ao longo do tempo.
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
        # fallback simples
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

    # Resumo interpretativo
    texto_resumo = _build_indicator_summary(serie_valid, row)
    st.markdown("**Resumo interpretativo do indicador**")
    st.write(texto_resumo)

    # Visualizações principais
    st.markdown("### 3. Distribuição do indicador")

    col_g1, col_g2 = st.columns(2)

    # Histograma
    with col_g1:
        st.write("**Distribuição (histograma)**")
        fig, ax = plt.subplots()
        ax.hist(serie_valid, bins="auto")
        ax.set_xlabel(indicador)
        ax.set_ylabel("Frequência")
        st.pyplot(fig)

    # Boxplot
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
            n_points = df_time.shape[0]
            suggested_freq = _suggest_time_freq(n_points)
            freq_map = _freq_options()
            reverse_map = {v: k for k, v in freq_map.items()}

            st.write(
                f"Total de registros de tempo: **{n_points}**. "
                f"Sugestão automática de agregação: **{_freq_label(suggested_freq)}**."
            )

            freq_label = st.selectbox(
                "Nível de agregação desejado:",
                options=list(freq_map.keys()),
                index=list(freq_map.values()).index(suggested_freq),
            )
            freq_code = freq_map[freq_label]

            # Agregação
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
                # Média móvel
                default_window = _default_rolling_window(freq_code)
                window = st.slider(
                    "Janela da média móvel (em número de períodos agregados):",
                    min_value=1,
                    max_value=max(2, min(12, len(ts_agg))),
                    value=min(default_window, max(2, len(ts_agg))),
                )

                ts_ma = ts_agg.rolling(window=window).mean()

                fig3, ax3 = plt.subplots()
                ax3.plot(ts_agg.index, ts_agg.values, label="Média agregada")
                ax3.plot(ts_ma.index, ts_ma.values, label="Média móvel")
                ax3.set_xlabel("Tempo")
                ax3.set_ylabel(indicador)
                ax3.legend()
                st.pyplot(fig3)

                # Limites naturais aproximados
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

    # Detalhamento técnico (drill-through)
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


def _fase_analisar(df: pd.DataFrame, types: dict) -> None:
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

    # -------------------------
    # 1. Correlação entre variáveis numéricas
    # -------------------------
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

                    # texto simples
                    top_var = corr_ord.index[0]
                    top_val = corr_ord.iloc[0]
                    st.write(
                        f"A variável com maior correlação com **{alvo}** é **{top_var}** "
                        f"(correlação de aproximadamente {top_val:.2f})."
                    )

                    # Scatter plot da relação mais forte
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

                        # linha de tendência simples (regressão linear)
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

    # -------------------------
    # 2. Pareto simples para categorias
    # -------------------------
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

            fig_p, ax_p = plt.subplots()

            # Barras de frequência
            x_labels = pareto_df.index.astype(str)
            ax_p.bar(x_labels, pareto_df["frequência"])
            ax_p.set_xlabel(cat_col)
            ax_p.set_ylabel("Frequência")
            ax_p.tick_params(axis="x", rotation=45)

            # Linha de % acumulado em eixo secundário
            ax2 = ax_p.twinx()
            ax2.plot(x_labels, pareto_df["acumulado_%"], marker="o")
            ax2.set_ylabel("% acumulado")
            ax2.set_ylim(0, 110)  # 0 a 110% pra dar uma folguinha visual

            st.pyplot(fig_p)


            # texto interpretativo
            top_n = min(3, len(pareto_df))
            principais = pareto_df.head(top_n)
            pct_top = principais["acumulado_%"].iloc[-1]

            st.write(
                f"As **{top_n}** categorias mais frequentes representam aproximadamente "
                f"**{pct_top:.1f}%** de todas as ocorrências. "
                "Essas categorias costumam ser um bom ponto de partida para priorização."
            )


def _fase_melhorar() -> None:
    st.markdown("## Fase I — Melhorar")
    st.write(
        """
Nesta fase, o foco é propor e testar melhorias no processo.

Em versões futuras, o PyTab poderá apoiar você com:
- comparação antes/depois (baseline vs. pós-melhoria),
- estimativa de impacto na média e na variabilidade,
- cenários simples "e se" para apoiar decisões.

Por enquanto, você pode:
- usar as medições atuais como baseline,
- exportar os resultados,
- e comparar com novas rodadas de dados após a implementação das melhorias.
"""
    )


def _fase_controlar() -> None:
    st.markdown("## Fase C — Controlar")
    st.write(
        """
Na fase de Controle, o objetivo é **garantir que os ganhos sejam sustentados**.

Versões futuras do PyTab poderão incluir:
- gráficos de controle (Ex.: XmR, X̄-R),
- monitoramento contínuo do indicador,
- alertas simples quando o processo sair do padrão.

Por enquanto, você pode:
- acompanhar regularmente o indicador usando a fase **Medir**,
- comparar novas medições com o baseline,
- e usar os gráficos para verificar se o processo continua estável.
"""
    )


# -----------------------------
# Interface principal
# -----------------------------
def main() -> None:
    st.set_page_config(
        page_title="PyTab - Open Statistical Toolkit",
        layout="wide",
    )

    # Cabeçalho com logo (se existir)
    logo_path = Path(__file__).parent.parent / "docs" / "assets" / "pytab_logo.png"

    with st.sidebar:
        if logo_path.exists():
            st.image(str(logo_path), width=140)
        st.markdown("### PyTab — DMAIC")
        st.write("Copiloto de análise para projetos Lean Six Sigma sem Minitab.")
        fase = st.radio(
            "Selecione a fase do projeto:",
            options=["Definir", "Medir", "Analisar", "Melhorar", "Controlar"],
            index=1,  # começa em Medir
        )
        st.markdown("---")
        st.caption(
            "Carregue um arquivo de dados na área principal para começar a usar o PyTab."
        )

    st.title("PyTab")
    st.write("Ferramenta aberta para análises estatísticas rápidas em qualquer CSV ou Excel.")
    st.markdown("---")

    # Upload de arquivo (comum a todas as fases)
    st.markdown("### Carregamento de dados")
    uploaded = st.file_uploader(
        "Selecione um arquivo de dados (CSV, TXT ou XLSX):",
        type=["csv", "txt", "xlsx"],
    )

    if uploaded is None:
        st.info("Envie um arquivo para iniciar a análise.")
        return

    # Leitura do DataFrame
    try:
        df = _load_dataframe(uploaded)
    except Exception as e:
        st.error(f"Falha ao ler o arquivo: {e}")
        return

    st.success(f"Arquivo carregado com sucesso. Formato: {uploaded.name}")
    st.write(f"**Dimensões do conjunto de dados:** {df.shape[0]} linhas × {df.shape[1]} colunas")

    st.markdown("#### Pré-visualização dos dados")
    st.dataframe(df.head())

    # Checagem de nomes das colunas
    issues = _check_column_names(df)
    if issues["empty"] or issues["duplicated"]:
        with st.expander("Avisos sobre os nomes das colunas"):
            if issues["empty"]:
                st.warning(
                    f"Foram encontradas {len(issues['empty'])} coluna(s) sem nome. "
                    "Considere renomeá-las para facilitar a análise."
                )
            if issues["duplicated"]:
                st.warning(
                    f"Foram encontradas colunas com nomes duplicados: {issues['duplicated']}."
                )

    # Detecção de tipos de coluna
    try:
        types = detect_column_types(df)
    except Exception:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
        categorical_cols = [
            c for c in df.columns if c not in numeric_cols + datetime_cols
        ]
        types = {
            "numeric": numeric_cols,
            "datetime": datetime_cols,
            "categorical": categorical_cols,
        }

    st.markdown("### Tipos de variáveis detectados")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Numéricas**")
        st.write(types.get("numeric") or "-")
    with col2:
        st.write("**Categóricas**")
        st.write(types.get("categorical") or "-")
    with col3:
        st.write("**Datas**")
        st.write(types.get("datetime") or "-")

    st.markdown("---")

    # Roteamento por fase DMAIC
    if fase == "Definir":
        _fase_definir()
    elif fase == "Medir":
        _fase_medir(df, types)
    elif fase == "Analisar":
        _fase_analisar(df, types)
    elif fase == "Melhorar":
        _fase_melhorar()
    elif fase == "Controlar":
        _fase_controlar()


if __name__ == "__main__":
    main()

