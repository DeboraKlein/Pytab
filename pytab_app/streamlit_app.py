from pathlib import Path

import pandas as pd
import streamlit as st

from pytab.charts.theme import apply_pytab_theme
from pytab.utils.app_utils import (
    check_column_names,
    detect_types,
    load_dataframe,
    show_column_warnings,
)
from pytab_app.fases.analisar.analisar import fase_analisar
from pytab_app.fases.controlar.controlar import fase_controlar
from pytab_app.fases.medir.medir import fase_medir
from pytab_app.fases.melhorar.melhorar import fase_melhorar


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

    # 1. TRECHO CSS DE IMPRESSÃO (Oculta menus do Streamlit ao gerar PDF pelo navegador)
    st.markdown(
        """
        <style>
        @media print {
            #MainMenu, header, footer, .stButton, [data-testid="stSidebar"] {
                display: none !important;
            }
            .main .block-container {
                max-width: 100% !important;
                padding: 1rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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

        # 2. TRECHO BOTÃO DE IMPRESSÃO (Adicionado na barra lateral)
        st.components.v1.html(
            """
            <button onclick="window.print()" style="
                width: 100%;
                background-color: #2E7D32;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                cursor: pointer;">
                🖨️ Imprimir / Salvar PDF
            </button>
            """,
            height=45,
        )

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
        fase_melhorar(df)
    elif fase == "Controlar":
        fase_controlar(df)


if __name__ == "__main__":
    main()
