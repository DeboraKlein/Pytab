import json
import numpy as np
import pandas as pd
from pathlib import Path

from pytab_app.modules.testes_estatisticos import (
    teste_t_uma_amostra,
    anova_oneway,
    regressao_linear_simples
)

TOL = 0.005  # tolerância percentual 0.5%

BASE_DIR = Path(__file__).resolve().parent
EXPECTED = json.loads((BASE_DIR / "expected_results.json").read_text())


def pct_diff(a, b):
    """Diferença percentual absoluta."""
    if a == 0 and b == 0:
        return 0
    return abs(a - b) / (abs(b) + 1e-9)


def validate_value(calc, expected, label, results):
    diff = pct_diff(calc, expected)

    passed = diff <= TOL
    results.append({
        "metric": label,
        "calculated": float(calc),
        "expected": float(expected),
        "pct_diff": float(diff),
        "status": "PASS" if passed else "FAIL"
    })


def validate_t_test(data, expected):
    results = []
    res = teste_t_uma_amostra(data, expected["mean"])

    validate_value(res["t_stat"], expected["t_stat"], "t_stat", results)
    validate_value(res["p_value"], expected["p_value"], "p_value", results)

    return results


def validate_anova(df, expected, numerica, categoria):
    results = []
    res = anova_oneway(df, numerica, categoria)

    validate_value(res["anova"]["F"][0], expected["f_stat"], "f_stat", results)
    validate_value(res["anova"]["PR(>F)"][0], expected["p_value"], "p_value", results)

    return results


def validate_regression(df, expected, x, y):
    results = []
    res = regressao_linear_simples(df[x], df[y])

    validate_value(res["slope"], expected["slope"], "slope", results)
    validate_value(res["intercept"], expected["intercept"], "intercept", results)
    validate_value(res["r2"], expected["r2"], "r2", results)

    return results


def run_all_validations():
    print("\n===============================")
    print("  VALIDANDO PyTab x Minitab")
    print("===============================\n")

    final_report = {}

    for filename, exp in EXPECTED.items():
        print(f"\n--- Dataset: {filename} ---")

        df = pd.read_csv(BASE_DIR / filename)
        report = []

        # Decide automaticamente o tipo de teste baseado no expected_results.json
        if "t_stat" in exp:
            report = validate_t_test(df.iloc[:, 0], exp)

        elif "f_stat" in exp:
            # ANOVA – detectar numérica e categórica automaticamente
            numerica = df.select_dtypes(include=["number"]).columns[0]
            categoria = df.select_dtypes(include=["object", "category"]).columns[0]
            report = validate_anova(df, exp, numerica, categoria)

        elif "slope" in exp:
            # Regressão
            cols = df.columns
            report = validate_regression(df, exp, cols[0], cols[1])

        else:
            report.append({"status": "UNKNOWN TEST TYPE"})

        final_report[filename] = report

        # Imprime no console
        for r in report:
            print(f"{r['metric']:12} | PyTab={r['calculated']:.4f} | "
                  f"Min={r['expected']:.4f} | diff={r['pct_diff']:.3%} "
                  f"| {r['status']}")

    # Salvar resultado consolidado
    outpath = BASE_DIR / "validation_report.json"
    outpath.write_text(json.dumps(final_report, indent=4))
    print(f"\nRelatório salvo em: {outpath}")


if __name__ == "__main__":
    run_all_validations()
