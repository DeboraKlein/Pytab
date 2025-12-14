import json
import math
from pathlib import Path

import pandas as pd

# ================================
# IMPORTS DO PYTAB (REAIS)
# ================================

from pytab_app.modules.testes_estatisticos import (
    teste_t_uma_amostra,
    teste_t_duas_amostras,
    teste_t_pareado,
    anova_oneway,
    teste_quiquadrado,
    teste_normalidade,
)

from pytab_app.fases.analisar.regressao import analisar_regressao
from pytab_app.fases.analisar.correlacao import calcular_correlacao

# ================================
# CONFIG
# ================================

BASE_DIR = Path(__file__).parent
DATASETS_DIR = BASE_DIR / "datasets"
EXPECTED_PATH = BASE_DIR / "expected_results.json"
REPORT_PATH = BASE_DIR / "validation_report.json"

TOL = 1e-3  # tolerância numérica aceitável


# ================================
# FUNÇÕES AUXILIARES
# ================================

def close(a, b, tol=TOL):
    return abs(a - b) <= tol


def pass_fail(a, b):
    return "PASS" if close(a, b) else "FAIL"


# ================================
# VALIDAÇÕES
# ================================

def validate_t_test_one_sample(df, expected):
    col = expected["column"]
    mu0 = expected["mu0"]

    res = teste_t_uma_amostra(df[col], mu0)

    return {
        "mean": pass_fail(res["mean"], expected["mean"]),
        "std": pass_fail(res["std"], expected["std"]),
        "t_stat": pass_fail(res["t_stat"], expected["t_stat"]),
        "p_value": pass_fail(res["p_value"], expected["p_value"]),
    }

def validate_t_test_two_samples(df, expected):
    num = expected["value_column"]
    cat = expected["group_column"]

    grupos = df[cat].dropna().unique()
    g1 = df[df[cat] == grupos[0]][num]
    g2 = df[df[cat] == grupos[1]][num]

    res = teste_t_duas_amostras(g1, g2)

    return {
        "t_stat": pass_fail(res["t_stat"], expected["t_stat"]),
        "p_value": pass_fail(res["p_value"], expected["p_value"]),
    }


def anova_oneway(df: pd.DataFrame, numerica: str, categoria: str) -> dict:
    data = df[[numerica, categoria]].dropna()

    modelo = smf.ols(f"`{numerica}` ~ C(`{categoria}`)", data=data).fit()
    tabela = sm.stats.anova_lm(modelo, typ=2)

    f_stat = tabela["F"].iloc[0]
    p_value = tabela["PR(>F)"].iloc[0]

    return {
        "teste": "anova_oneway",
        "n": int(len(data)),
        "mean": float(data[numerica].mean()),
        "std": float(data[numerica].std(ddof=1)),
        "t_stat": None,
        "f_stat": float(f_stat),
        "p_value": float(p_value),
        "anova": tabela,
    }





def validate_regression(df, expected):
    res = regressao_linear_simples(df, expected["x"], expected["y"])

    return {
        "slope": pass_fail(res["coef_angular"], expected["slope"]),
        "intercept": pass_fail(res["intercepto"], expected["intercept"]),
        "r2": pass_fail(res["r2"], expected["r2"]),
    }


def validate_correlation(df, expected):
    corr = analisar_correlacao(df)["corr"]

    out = {}
    for (a, b), val in expected["pairs"].items():
        out[f"{a}~{b}"] = pass_fail(corr.loc[a, b], val)

    return out


# ================================
# MAIN
# ================================

def main():
    with open(EXPECTED_PATH) as f:
        expected_all = json.load(f)

    report = {}

    for fname, expected in expected_all.items():
        csv_path = DATASETS_DIR / fname
        df = pd.read_csv(csv_path)

        tipo = expected["type"]

        if tipo == "t_test_one_sample":
            report[fname] = validate_t_test_one_sample(df, expected)

        elif tipo == "t_test_two_samples":
            report[fname] = validate_t_test_two_samples(df, expected)

        elif tipo == "anova_oneway":
            report[fname] = anova_oneway(df, expected)

        elif tipo == "regression_linear_simple":
            report[fname] = validate_regression(df, expected)

        elif tipo == "correlation":
            report[fname] = validate_correlation(df, expected)

        else:
            report[fname] = {"status": "SKIPPED", "reason": "Tipo não implementado"}

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=4)

    print("Validação concluída.")
    print(f"Relatório salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()
