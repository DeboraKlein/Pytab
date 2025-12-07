import matplotlib.pyplot as plt

PRIMARY_BLUE = "#1f77b4"
SECONDARY_ORANGE = "#ec7f00"

def apply_pytab_theme():
    plt.style.use("default")

    plt.rcParams.update({
        # cores PyTab
        "axes.prop_cycle": plt.cycler(color=[PRIMARY_BLUE, SECONDARY_ORANGE]),

        # sem fundo branco
        "axes.facecolor": "none",
        "figure.facecolor": "none",

        # eixos limpos
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#333333",
        "xtick.color": "#333333",
        "ytick.color": "#333333",

        # grid removido
        "axes.grid": False,
        "grid.color": "none",

        # texto legível
        "font.size": 11,
    })

