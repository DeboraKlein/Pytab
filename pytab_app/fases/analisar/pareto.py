import pandas as pd
import matplotlib.pyplot as plt
from pytab.charts.theme import PRIMARY, SECONDARY, apply_pytab_theme

apply_pytab_theme()


def analisar_pareto(df):
    """
    Retorna:
    - fig: figura do Pareto
    - tabela: dataframe com valores e % acumulado
    """

    # ---------------------------------------------------------
    # Seleção da coluna categórica
    # ---------------------------------------------------------
    cat_cols = df.select_dtypes(include=["object", "category"]).columns

    if len(cat_cols) == 0:
        return None, None

    coluna = cat_cols[0]  # simples por enquanto

    serie = df[coluna].dropna()

    if serie.empty:
        return None, None

    # ---------------------------------------------------------
    # Cálculo do Pareto
    # ---------------------------------------------------------
    contagens = serie.value_counts()
    valores = contagens.values
    categorias = contagens.index

    contrib_pct = valores / valores.sum() * 100
    acum_pct = contrib_pct.cumsum()

    tabela = pd.DataFrame({
        "Categoria": categorias,
        "Frequência": valores,
        "%": contrib_pct.round(2),
        "% Acumulado": acum_pct.round(2)
    })

    # ---------------------------------------------------------
    # Gráfico Pareto
    # ---------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.bar(categorias, valores, color=PRIMARY)
    ax1.set_ylabel("Frequência", color=PRIMARY)
    ax1.set_xticklabels(categorias, rotation=30, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(categorias, acum_pct, color=SECONDARY, marker="o", linewidth=2)
    ax2.set_ylabel("% Acumulado", color=SECONDARY)
    ax2.set_ylim(0, 110)

    ax1.grid(axis="y", alpha=0.25)
    ax2.grid(False)

    fig.tight_layout()

    return fig, tabela


