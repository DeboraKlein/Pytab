import json
from pathlib import Path

import pandas as pd

from pytab_app.modules.testes_estatisticos import (
    teste_t_uma_amostra,
    teste_t_duas_amostras,
    teste_t_pareado,
    anova_oneway,
    teste_quiquadrado,
    teste_normalidade,
)

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


def _load_dataset(fname: str) -> tuple[pd.DataFrame | None, str | None]:
    """
    Carrega o dataset. Se não existir com o nome exato,
    tenta alternativas simples para reduzir fricção.
    Retorna (df, resolved_name) ou (None, None).
    """
    candidates = [
        fname,
        fname.replace("_dataset", ""),
        fname.replace("_dataset", "").replace(".csv", "_dataset.csv"),
    ]

    for cand in candidates:
        p = DATASETS_DIR / cand
        if p.exists():
            return pd.read_csv(p), cand

    return None, None


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


def validate_t_test_paired(df, expected):
    b = expected["before_column"]
    a = expected["after_column"]

    res = teste_t_pareado(df[b], df[a])

    return {
        "t_stat": pass_fail(res["t_stat"], expected["t_stat"]),
        "p_value": pass_fail(res["p_value"], expected["p_value"]),
        "diff_mean": pass_fail(res.get("diff_mean", res["mean"]), expected["diff_mean"]),
    }


def validate_anova(df, expected):
    # IMPORTANTÍSSIMO: aqui precisam ser nomes reais de colunas no CSV.
    num_col = expected["numeric_column"]
    cat_col = expected["category_column"]

    res = anova_oneway(df, numerica=num_col, categoria=cat_col)

    return {
        "f_stat": pass_fail(res["f_stat"], expected["f_stat"]),
        "p_value": pass_fail(res["p_value"], expected["p_value"]),
    }


def validate_normality(df, expected):
    col = expected["column"]

    res = teste_normalidade(df[col], metodo="shapiro")

    return {
        "w_stat": pass_fail(res.get("w_stat", res["t_stat"]), expected["w_stat"]),
        "p_value": pass_fail(res["p_value"], expected["p_value"]),
    }


def validate_chi_square(df, expected):
    r = expected["row_var"]
    c = expected["col_var"]

    res = teste_quiquadrado(df, r, c)

    return {
        "chi2": pass_fail(res["f_stat"], expected["chi2"]),
        "p_value": pass_fail(res["p_value"], expected["p_value"]),
        "dof": "PASS" if int(res["dof"]) == int(expected["dof"]) else "FAIL",
    }


# ================================
# MAIN
# ================================

def main():
    with open(EXPECTED_PATH, encoding="utf-8") as f:
        expected_all = json.load(f)

    report = {}

    for fname, expected in expected_all.items():
        df, resolved_name = _load_dataset(fname)

        if df is None:
            report[fname] = {"status": "SKIPPED", "reason": "Dataset não encontrado em validation/datasets"}
            continue

        tipo = expected["type"]

        try:
            if tipo == "t_test_one_sample":
                report[fname] = validate_t_test_one_sample(df, expected)

            elif tipo == "t_test_two_samples":
                report[fname] = validate_t_test_two_samples(df, expected)

            elif tipo == "t_test_paired":
                report[fname] = validate_t_test_paired(df, expected)

            elif tipo == "anova_oneway":
                report[fname] = validate_anova(df, expected)

            elif tipo == "normality_shapiro":
                report[fname] = validate_normality(df, expected)

            elif tipo == "chi_square_independence":
                report[fname] = validate_chi_square(df, expected)

            else:
                # ainda não implementados neste validate_suite
                report[fname] = {"status": "SKIPPED", "reason": f"Tipo não implementado: {tipo}"}

        except Exception as e:
            report[fname] = {"status": "ERROR", "reason": str(e), "dataset": resolved_name}

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("Validação concluída.")
    print(f"Relatório salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()

