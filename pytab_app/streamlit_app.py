"""
Aplicativo Streamlit do PyTab
Interface para usuários finais.
"""

from pathlib import Path
import tempfile

import matplotlib.pyplot as plt
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


# -----------------------------
# Interface principal
# -----------------------------
def main() -> None:
    st.set_page_config(
        page_title="PyTab - Open Statistical Toolkit",
        layout="wide",
    )

    # Cabeçalho com logo (se existir)
    logo_path = Path(__file__).parent.parent / "docs" / "assets" / "Logo_PyTab.jpg"
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=180)
    with col_title:
        st.title("PyTab")
        st.write(
            "Ferramenta aberta para análises estatísticas rápidas em qualquer CSV ou Excel."
        )

    st.markdown("---")

    # Upload de arquivo
    st.markdown("### 1. Carregamento de dados")
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

    # Detecção de tipos de coluna (numérico, categórico, datas)
    try:
        types = detect_column_types(df)
        numeric_cols = types.get("numeric", [])
        categorical_cols = types.get("categorical", [])
        datetime_cols = types.get("datetime", [])
    except Exception:
        # fallback simples, caso detect_column_types mude no futuro
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
        categorical_cols = [
            c for c in df.columns if c not in numeric_cols + datetime_cols
        ]

    st.markdown("### 2. Tipos de variáveis detectados")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Numéricas**")
        st.write(numeric_cols or "-")
    with col2:
        st.write("**Categóricas**")
        st.write(categorical_cols or "-")
    with col3:
        st.write("**Datas**")
        st.write(datetime_cols or "-")

    st.markdown("---")

    # -----------------------------
    # Abas de análise
    # -----------------------------
    tab_indicador, tab_grupos, tab_relacao = st.tabs(
        [
            "Análise de um indicador",
            "Comparar grupos (em breve)",
            "Relação entre variáveis (em breve)",
        ]
    )

    # =============================
    #  Aba 1 - Análise de um indicador
    # =============================
    with tab_indicador:
        st.markdown("### 3. Escolha do indicador")
        if not numeric_cols:
            st.info(
                "Nenhuma coluna numérica foi identificada. "
                "Verifique se o arquivo contém dados numéricos."
            )
        else:
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
            else:
                st.markdown("### 4. Estatísticas e interpretação")

                # Estatísticas descritivas (usando summarize_numeric)
                summary_all = summarize_numeric(df)
                if isinstance(summary_all, pd.DataFrame) and indicador in summary_all.index:
                    row = summary_all.loc[indicador]
                else:
                    # fallback simples, caso summarize_numeric tenha outro formato
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

                # KPI cards
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Quantidade de valores válidos", int(row.get("count", len(serie_valid))))
                with k2:
                    st.metric("Média", f"{row.get('mean', serie_valid.mean()):.2f}")
                with k3:
                    st.metric("Mediana", f"{row.get('median', serie_valid.median()):.2f}")
                with k4:
                    st.metric("Desvio padrão", f"{row.get('std', serie_valid.std()):.2f}")

                # Texto interpretativo amigável
                texto_resumo = _build_indicator_summary(serie_valid, row)
                st.markdown("**Resumo interpretativo do indicador**")
                st.write(texto_resumo)

                # Gráficos principais
                st.markdown("### 5. Visualizações")

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

                # Série temporal (se houver coluna de data)
                if datetime_cols:
                    st.markdown("### 6. Evolução ao longo do tempo (se aplicável)")
                    col_dt1, col_dt2 = st.columns([2, 3])
                    with col_dt1:
                        data_col = st.selectbox(
                            "Se existir uma coluna de data/tempo associada, selecione-a:",
                            options=datetime_cols,
                        )
                    with col_dt2:
                        st.write(
                            "Abaixo, a evolução do indicador ao longo do tempo, "
                            "usando a coluna de data selecionada."
                        )

                    df_time = df[[data_col, indicador]].copy()
                    df_time[data_col] = pd.to_datetime(df_time[data_col], errors="coerce")
                    df_time = df_time.dropna(subset=[data_col])
                    df_time = df_time.sort_values(data_col)

                    if not df_time.empty:
                        st.line_chart(
                            df_time.set_index(data_col)[indicador],
                            use_container_width=True,
                        )
                    else:
                        st.info(
                            "Não foi possível gerar a série temporal com os dados atuais "
                            "(datas inválidas ou ausentes)."
                        )

                # Outliers
                st.markdown("### 7. Detecção de valores muito fora do padrão (outliers)")

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

                # Texto “humano + técnico”
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

    # =============================
    #  Aba 2 - Comparar grupos (em breve)
    # =============================
    with tab_grupos:
        st.markdown("### Comparar grupos (em breve)")
        st.info(
            "Esta aba será usada para comparar o comportamento de um indicador entre grupos, "
            "como meses, categorias, unidades, tratamentos, etc."
        )

    # =============================
    #  Aba 3 - Relação entre variáveis (em breve)
    # =============================
    with tab_relacao:
        st.markdown("### Relação entre variáveis (em breve)")
        st.info(
            "Aqui você poderá explorar se uma variável ajuda a explicar outra, "
            "por exemplo, usando gráficos de dispersão e regressão linear simples."
        )


if __name__ == "__main__":
    main()

