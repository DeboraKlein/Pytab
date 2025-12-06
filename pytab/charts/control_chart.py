"""
pytab.charts.control_chart
--------------------------
Estrutura inicial para gráficos de controle (SPC).

Versão 0.1.0:
- Função base que calcula média e desvio.
- Placeholder para limites de controle.
- Plot opcional futuramente (matplotlib ou plotly).

Versões futuras:
- XmR
- Média Móvel
- P-chart, U-chart
- Interface com o Streamlit
"""

import pandas as pd


def calculate_basic_control_limits(series: pd.Series) -> dict:
    """
    Calcula média, desvio padrão e limites teóricos iniciais.
    (Não é SPC completo ainda.)

    Retorna:
        {
            "mean": valor,
            "std": valor,
            "ucl": valor,
            "lcl": valor
        }
    """

    mean = series.mean()
    std = series.std()

    return {
        "mean": mean,
        "std": std,
        "ucl": mean + 3 * std,
        "lcl": mean - 3 * std,
    }
