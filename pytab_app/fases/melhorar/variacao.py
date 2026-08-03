import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calcular_variacao(serie: pd.Series):
    # Remove nulos e converte para numérico para evitar erros de tipo
    serie_limpa = pd.to_numeric(serie, errors="coerce").dropna()

    ponto_corte = len(serie_limpa) // 2
    antes = serie_limpa.iloc[:ponto_corte]
    depois = serie_limpa.iloc[ponto_corte:]

    var_antes = antes.std()
    var_depois = depois.std()

    mudança = var_antes - var_depois

    # Cálculo percentual da variação para agregar valor ao resumo
    pct_reducao = (mudança / var_antes * 100) if var_antes > 0 else 0

    resumo = {
        "Desvio padrão antes": var_antes,
        "Desvio padrão depois": var_depois,
        "Redução absoluta da variação": mudança,
        "Redução percentual (%)": pct_reducao,
        "Conclusão": (
            "A variação diminuiu — processo mais estável."
            if mudança > 0
            else "A variação aumentou — investigar causas."
        ),
    }

    return antes, depois, resumo


def grafico_variacao(antes, depois):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Boxplot estilizado
    bp = ax.boxplot(
        [antes, depois],
        tick_labels=["Antes", "Depois"],
        patch_artist=True,
        showmeans=True,
    )

    # Cores personalizadas: Azul para 'Antes' (baseline) e Verde para 'Depois' (melhoria)
    cores = ["#4A90E2", "#50E3C2"]
    for patch, color in zip(bp["boxes"], cores):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Ajustes estéticos
    ax.set_title("Comparativo de Variação (Antes vs. Depois)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Valores da Métrica", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    return fig