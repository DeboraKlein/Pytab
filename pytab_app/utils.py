from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from pytab.io.reader import read_any
from pytab.utils.schema import detect_column_types


def load_dataframe(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """
    Salva o arquivo enviado em disco temporário e delega leitura ao read_any.
    """
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    df = read_any(temp_path)
    return df


def check_column_names(df: pd.DataFrame) -> dict:
    """
    Verifica nomes de colunas vazios ou duplicados.
    Retorna {"empty": [...], "duplicated": [...]}
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


def detect_types(df: pd.DataFrame) -> dict:
    """
    Usa detect_column_types, com fallback simples se der erro.
    Retorna dict com chaves: numeric, datetime, categorical.
    """
    try:
        types = detect_column_types(df)
        return types
    except Exception:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
        categorical_cols = [
            c for c in df.columns if c not in numeric_cols + datetime_cols
        ]
        return {
            "numeric": numeric_cols,
            "datetime": datetime_cols,
            "categorical": categorical_cols,
        }


def show_column_warnings(issues: dict) -> None:
    """
    Mostra avisos de colunas sem nome ou duplicadas no Streamlit.
    """
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
