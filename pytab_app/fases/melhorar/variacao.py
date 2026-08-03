import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats


def calcular_variacao(serie: pd.Series):
    # Remove nulos e converte para numérico para evitar erros de tipo
    serie_limpa = pd.to_numeric(serie, errors="coerce").dropna()

    ponto_corte = len(serie_limpa) // 2
    antes = serie_limpa.iloc[:ponto_corte]
    depois = serie_limpa.iloc[ponto_corte:]

    var_antes = antes.var(ddof=1)
    var_depois = depois.var(ddof=1)

    std_antes = antes.std()
    std_depois = depois.std()

    mudanca = std_antes - std_depois
    pct_reducao = (mudanca / std_antes * 100) if std_antes > 0 else 0

    # 🧪 Cálculo do Teste F (Comparação de Variâncias)
    f_stat = var_antes / var_depois if var_depois > 0 else np.nan
    df1 = len(antes) - 1
    df2 = len(depois) - 1
    p_valor = (
        1 - stats.f.cdf(f_stat, df1, df2) if not np.isnan(f_stat) else 1.0
    )

    resumo = {
        "Desvio padrão antes": std_antes,
        "Desvio padrão depois": std_depois,
        "Redução absoluta da variação": mudanca,
        "Redução percentual (%)": pct_reducao,
        "Estatística F": f_stat,
        "p-valor (Teste F)": p_valor,
        "Conclusão": (
            "A redução da variação foi estatisticamente significativa! (p < 0.05)"
            if p_valor < 0.05
            else "A variação diminuiu, mas não é estatisticamente significativa (p ≥ 0.05)."
            if mudanca > 0
            else "A variação aumentou — investigar causas."
        ),
    }

    return antes, depois, resumo


def grafico_variacao(antes, depois):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Boxplot estilizado com a correção do tick_labels
    bp = ax.boxplot(
        [antes, depois],
        tick_labels=["Antes", "Depois"],
        patch_artist=True,
        showmeans=True,
    )

    # Cores personalizadas do PyTab
    cores = ["#1f77b4", "#ec7f00"]
    for patch, color in zip(bp["boxes"], cores):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Ajustes estéticos
    ax.set_title(
        "Comparativo de Variação (Antes vs. Depois)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_ylabel("Valores da Métrica", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    return fig