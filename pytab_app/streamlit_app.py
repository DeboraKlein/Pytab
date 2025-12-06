# pytab_app/streamlit_app.py

import streamlit as st
import pandas as pd

from pytab.io.reader import read_any
from pytab.stats.descriptive import summarize_numeric

def main():
    st.title("PyTab – Análise Estatística Rápida")

    st.markdown(
        "Carregue um arquivo CSV ou Excel e o PyTab fará uma análise estatística básica."
    )

    uploaded_file = st.file_uploader("Selecione um arquivo (.csv, .txt, .xlsx)", type=["csv", "txt", "xlsx"])

    if uploaded_file is not None:
        # Salva temporariamente para reutilizar a função read_any
        with open("temp_upload", "wb") as f:
            f.write(uploaded_file.read())

        try:
            df = read_any("temp_upload")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return

        st.subheader("Prévia dos dados")
        st.dataframe(df.head())

        st.subheader("Estatísticas descritivas (colunas numéricas)")
        summary = summarize_numeric(df)
        if summary.empty:
            st.info("Nenhuma coluna numérica encontrada.")
        else:
            st.dataframe(summary)

        # Futuro: gráficos, SPC, Pareto, relatórios etc.

if __name__ == "__main__":
    main()
