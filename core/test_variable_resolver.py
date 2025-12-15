import pandas as pd

from .validation.variable_resolver import resolve_variables


def test_resolve_anova_basic():
    """
    Deve escolher:
    - 1 numérica com maior n / variância
    - 1 categórica com menor cardinalidade válida
    """
    df = pd.DataFrame({
        "Revenue": [10, 12, 11, 20, 22, 21],
        "Cost": [7, 8, 7, 14, 15, 14],
        "Plant": ["A", "A", "A", "B", "B", "B"],
        "ID": [1, 2, 3, 4, 5, 6],
    })

    vars_ = resolve_variables(df, "anova_oneway")

    assert vars_["numeric"] in {"Revenue", "Cost"}
    assert vars_["factor"] == "Plant"
