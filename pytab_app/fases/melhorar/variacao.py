import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calcular_variacao(serie: pd.Series):
    antes = serie.iloc[: len(serie)//2]
    depois = serie.iloc[len(serie)//2 :]

    var_antes = antes.std()
    var_depois = depois.std()

    mudança = var_antes - var_depois

    resumo = {
        "Desvio padrão antes": var_antes,
        "Desvio padrão depois": var_depois,
        "Redução da variação": mudança,
        "Conclusão": (
            "A variação diminuiu — processo mais estável."
            if mudança > 0
            else "A variação aumentou — investigar causas."
        )
    }

    return antes, depois, resumo


def grafico_variacao(antes, depois):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.boxplot([antes, depois], labels=["Antes", "Depois"])
    ax.set_title("Redução de variação")
    return fig
