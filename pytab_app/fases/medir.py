import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pytab.theme import apply_pytab_theme

apply_pytab_theme()

PRIMARY = "#1f77b4"
SECONDARY = "#ec7f00"



def fase_medir(df: pd.DataFrame):
    st.header("Fase Medir — Estatísticas e Comportamento do Indicador")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.warning("Nenhuma coluna numérica encontrada no dataset.")
        return

    indicador = st.selectbox("Selecione o indicador numérico", numeric_cols)

    col1, col2, col3 = st.columns(3)
    with col1:
        agg = st.selectbox("Agrupamento temporal", ["Diário", "Semanal", "Mensal", "Trimestral", "Anual"])
    with col2:
        rolling = st.checkbox("Incluir Média Móvel", value=True)
    with col3:
        janela = st.number_input("Janela Média Móvel", min_value=2, max_value=60, value=7)

    # Conversão de datas (caso existam colunas de data)
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    if date_cols:
        date_col = date_cols[0]
        df_sorted = df.sort_values(by=date_col)
    else:
        st.error("Nenhuma coluna de data encontrada. A Fase Medir exige pelo menos uma coluna de datas.")
        return

    # Agregação temporal
    df_temp = df_sorted.set_index(date_col).resample(
        {"Diário": "D", "Semanal": "W", "Mensal": "M", "Trimestral": "Q", "Anual": "Y"}[agg]
    )[indicador].mean().dropna()

    # Estatísticas
    st.subheader("Estatísticas descritivas")
    st.dataframe(df_temp.describe().T)

    # Gráfico principal
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_temp.index, df_temp.values, color=PRIMARY, linewidth=2, label="Valor médio")

    if rolling:
        df_roll = df_temp.rolling(janela).mean()
        ax.plot(df_roll.index, df_roll.values, color=SECONDARY, linewidth=2, linestyle="--", label=f"Média móvel ({janela})")

    ax.set_title(f"{indicador} — Série Temporal ({agg})")
    ax.set_xlabel("Tempo")
    ax.set_ylabel(indicador)
    ax.legend()
    ax.grid(True, alpha=0.25)

    st.pyplot(fig)
    plt.close(fig)
