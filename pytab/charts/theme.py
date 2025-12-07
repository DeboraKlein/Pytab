"""
Tema visual padrão do PyTab para gráficos matplotlib.
Aplica um estilo corporativo com fundo cinza suave e linhas grafite.
"""

import matplotlib.pyplot as plt


def apply_pytab_style() -> None:
    """Aplica o tema global do PyTab no matplotlib."""
    plt.rcParams.update(
        {
            # Fundo
            "figure.facecolor": "none",      # deixa o Streamlit controlar o fundo externo
            "axes.facecolor": "#f5f5f5",     # cinza suave dentro do gráfico

            # Cores de texto / eixos
            "axes.edgecolor": "#333333",
            "axes.labelcolor": "#333333",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "text.color": "#333333",

            # Linhas padrão
            "lines.color": "#333333",
            "axes.prop_cycle": plt.cycler(color=["#333333"]),

            # Grade
            "axes.grid": True,
            "grid.color": "#dddddd",
            "grid.linestyle": "-",
            "grid.linewidth": 0.5,

            # Fonte
            "font.size": 10,

            # Layout
            "figure.autolayout": True,
        }
    )
