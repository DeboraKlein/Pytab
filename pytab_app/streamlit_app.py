from pathlib import Path

import streamlit as st
import pandas as pd

from pytab.charts.theme import apply_pytab_theme
from pytab.utils.app_utils import (
    load_dataframe,
    check_column_names,
    detect_types,
    show_column_warnings
)
from pytab_app.fases.medir import fase_medir
from pytab_app.fases.analisar import fase_analisar
from pytab_app.fases.melhorar import fase_melhorar
from pytab_app.fases.controlar import fase_controlar


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


def main() -> None:
    apply_pytab_theme()

    st.set_page_config(
        page_title="PyTab - Open Statistical Toolkit",
        layout="wide",
    )

    logo_path = Path(__file__).parent.parent / "docs" / "assets" / "Pytab_logo.svg"

    with st.sidebar:
        if logo_path.exists():
            st.image(str(logo_path), width=140)
        st.markdown("### PyTab — DMAIC")
        st.write("Copiloto de análise para projetos Lean Six Sigma sem Minitab.")
        fase = st.radio(
            "Selecione a fase do projeto:",
            options=["Definir", "Medir", "Analisar", "Melhorar", "Controlar"],
            index=1,
        )
        st.markdown("---")
        st.caption(
            "Carregue um arquivo de dados na área principal para começar a usar o PyTab."
        )

    st.title("PyTab")
    st.write("Ferramenta aberta para análises estatísticas rápidas em qualquer CSV ou Excel.")
    st.markdown("---")

    st.markdown("### Carregamento de dados")
    uploaded = st.file_uploader(
        "Selecione um arquivo de dados (CSV, TXT ou XLSX):",
        type=["csv", "txt", "xlsx"],
    )

    if uploaded is None:
        st.info("Envie um arquivo para iniciar a análise.")
        return

    try:
        df = load_dataframe(uploaded)
    except Exception as e:
        st.error(f"Falha ao ler o arquivo: {e}")
        return

    st.success(f"Arquivo carregado com sucesso. Formato: {uploaded.name}")
    st.write(f"**Dimensões do conjunto de dados:** {df.shape[0]} linhas × {df.shape[1]} colunas")

    st.markdown("#### Pré-visualização dos dados")
    st.dataframe(df.head())

    issues = check_column_names(df)
    show_column_warnings(issues)

    types = detect_types(df)

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

    if fase == "Definir":
        _fase_definir()
    elif fase == "Medir":
        fase_medir(df)
    elif fase == "Analisar":
        fase_analisar(df)
    elif fase == "Melhorar":
        fase_melhorar(df, types)
    elif fase == "Controlar":
        fase_controlar(df, types)


if __name__ == "__main__":
    main()
