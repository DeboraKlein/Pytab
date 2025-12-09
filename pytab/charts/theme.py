"""
Tema visual do PyTab para Matplotlib e Plotly.
"""

import matplotlib.pyplot as plt

# Paleta corporativa do PyTab
PRIMARY = "#1f77b4"       # Azul técnico
SECONDARY = "#ec7f00"     # Laranja técnico
TEXT_COLOR = "#333333"    # Grafite
BG_COLOR = "#ffffff"      # Fundo branco padrão

def apply_pytab_theme():
    """
    Configura o tema do Matplotlib.
    """
    plt.style.use("default")

    plt.rcParams.update({
        "figure.facecolor": BG_COLOR,
        "axes.facecolor": BG_COLOR,
        "axes.edgecolor": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "text.color": TEXT_COLOR,
        "grid.color": "#cccccc",
        "axes.grid": False,
    })

def style_plotly(fig):
    """
    Aplica estilo consistente para figuras Plotly.
    """
    fig.update_layout(
        font=dict(color=TEXT_COLOR),
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        legend=dict(
            font=dict(color=TEXT_COLOR, size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        tickfont=dict(color=TEXT_COLOR, size=11),
        title_font=dict(color=TEXT_COLOR, size=12),
        showgrid=False,
    )

    fig.update_yaxes(
        tickfont=dict(color=TEXT_COLOR, size=11),
        title_font=dict(color=TEXT_COLOR, size=12),
        showgrid=False,
    )

    return fig


