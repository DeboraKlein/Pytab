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


if __name__ == "__main__":
    main()

