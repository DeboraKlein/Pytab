# pytab_app/streamlit_app.py

from pathlib import Path
import streamlit as st

from pytab.io.reader import read_any
from pytab.stats.descriptive import summarize_numeric


def main():
    # Caminho do logo relativo a este arquivo
    logo_path = Path(__file__).parent.parent / "docs" / "assets" / "pytab_logo.png"

    st.image(str(logo_path), width=250)
    st.title("PyTab – Open Statistical Toolkit")
    st.markdown("Análises estatísticas rápidas para Lean Six Sigma, qualidade e dados em geral.")
    ...


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
