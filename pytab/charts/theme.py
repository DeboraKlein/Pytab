import matplotlib.pyplot as plt

PRIMARY_BLUE = "#1f77b4"
SECONDARY_ORANGE = "#ec7f00"

def apply_pytab_theme():
    plt.style.use("default")

    plt.rcParams.update({
        # Cores PyTab
        "axes.prop_cycle": plt.cycler(color=[PRIMARY_BLUE, SECONDARY_ORANGE]),

        # Fundo limpo e compatível com Streamlit
        "figure.facecolor": "white",     # <— ALTERAÇÃO IMPORTANTE
        "axes.facecolor": "none",

        # Eixos limpos
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#333333",
        "xtick.color": "#333333",
        "ytick.color": "#333333",

        # Grid removido
        "axes.grid": False,
        "grid.color": "none",

        # Texto legível
        "font.size": 11,
    })


