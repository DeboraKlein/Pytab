"""
Aplicativo Streamlit do PyTab
Interface para usuários finais.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from pytab.io.reader import read_any
from pytab.stats.descriptive import summarize_numeric
from pytab.utils.schema import detect_column_types
from pytab.stats.outliers import detect_outliers


def _save_uploaded_file(uploaded_file) -> Path:
    """
    Salva o arquivo enviado em disco e retorna o Path.
    (Simples, mas suficiente para uso local.)
    """
    temp_path = Path("temp_upload") / uploaded_file.name
    temp_path.parent.mkdir(exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    return temp_path


def main():
    # Logo
    logo_path = Path(__file__).parent.parent / "docs" / "assets" / "pytab_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=320)

    st.title("PyTab – Open Statistical Toolkit")
    st.markdown(
        "Análises estatísticas rápidas para dados reais, com foco em qualidade, Lean Six Sigma e tomada de decisão."
    )

    st.markdown("### 1. Envie um arquivo de dados")
    uploaded = st.file_uploader(
        "Arquivos aceitos: CSV, TXT, XLSX",
        type=["csv", "txt", "xlsx"],
    )

    if uploaded is None:
        st.info("Envie um arquivo para começar a análise.")
        return

    # Salva e lê com PyTab
    temp_path = _save_uploaded_file(uploaded)

    try:
        df = read_any(str(temp_path))
    except Exception as e:
        st.error(f"Não foi possível ler o arquivo: {e}")
        return

    st.markdown("### 2. Prévia dos dados")
    st.write(f"**Formato:** {df.shape[0]} linhas x {df.shape[1]} colunas")
    st.dataframe(df.head())

    # Tipos de colunas
    st.markdown("### 3. Detecção de tipos de colunas")
    types = detect_column_types(df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Numéricas**")
        st.write(types["numeric"] or "-")
    with col2:
        st.write("**Categóricas**")
        st.write(types["categorical"] or "-")
    with col3:
        st.write("**Datas**")
        st.write(types["datetime"] or "-")

    # Estatísticas descritivas
    st.markdown("### 4. Estatísticas descritivas (colunas numéricas)")
    summary = summarize_numeric(df)
    if isinstance(summary, pd.DataFrame) and not summary.empty:
        st.dataframe(summary)
    else:
        st.info("Nenhuma coluna numérica encontrada para cálculo estatístico.")

    # -----------------------------
    # Outliers
    # -----------------------------
    st.markdown("### 5. Detecção de outliers")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.info("Nenhuma coluna numérica disponível para análise de outliers.")
        return

    col_sel, col_method = st.columns(2)
    with col_sel:
        target_col = st.selectbox(
            "Selecione a coluna numérica para analisar outliers:",
            options=numeric_cols,
        )
    with col_method:
        method = st.selectbox(
            "Método de detecção:",
            options=["zscore", "iqr"],
            format_func=lambda x: "Z-score" if x == "zscore" else "IQR (quartis)",
        )

    if method == "zscore":
        threshold = st.slider(
            "Limite de |z-score| para considerar outlier:",
            min_value=2.0,
            max_value=5.0,
            value=3.0,
            step=0.1,
        )
        result = detect_outliers(
            df[target_col],
            method="zscore",
            threshold=threshold,
        )
    else:  # IQR
        factor = st.slider(
            "Fator do IQR:",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
        )
        result = detect_outliers(
            df[target_col],
            method="iqr",
            factor=factor,
        )

    summary_out = result["summary"]
    st.write(
        f"**Total de valores válidos:** {summary_out['n']}  \n"
        f"**Outliers detectados:** {summary_out['n_outliers']} "
        f"({summary_out['pct_outliers']}%)"
    )

    outliers_df = result["outliers"]
    if not outliers_df.empty:
        st.markdown("**Tabela de outliers detectados**")
        st.dataframe(outliers_df)
    else:
        st.info("Nenhum outlier foi detectado com os parâmetros atuais.")



if __name__ == "__main__":
    main()

