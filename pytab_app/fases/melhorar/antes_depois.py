import pandas as pd
import matplotlib.pyplot as plt


def analisar_antes_depois(df, col_data, col_valor, data_corte):
    df_sorted = df.sort_values(col_data)

    antes = df_sorted[df_sorted[col_data] < pd.to_datetime(data_corte)][col_valor]
    depois = df_sorted[df_sorted[col_data] >= pd.to_datetime(data_corte)][col_valor]

    media_antes = antes.mean()
    media_depois = depois.mean()

    resumo = pd.DataFrame({
        "Fase": ["Antes", "Depois"],
        "Média": [media_antes, media_depois],
        "Contagem": [len(antes), len(depois)]
    })

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(["Antes", "Depois"], [media_antes, media_depois], color=["#1f77b4", "#ec7f00"])
    ax.set_title("Comparação Antes vs Depois")
    ax.set_ylabel(col_valor)

    return resumo, fig
