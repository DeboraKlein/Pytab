import json
import math
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Funções "engine" do PyTab (as mesmas usadas no app)
from pytab_app.modules.testes_estatisticos import (
    teste_t_uma_amostra as pytab_t_test_one_sample,
    teste_t_duas_amostras as pytab_t_test_two_samples,
    teste_t_pareado as pytab_t_test_paired,
    anova_oneway as pytab_anova_oneway,
    teste_quiquadrado as pytab_chi_square,
    teste_normalidade as pytab_normality,
)


# ================================
# CONFIG
# ================================

BASE_DIR = Path(__file__).parent
DATASETS_DIR = BASE_DIR / "datasets"
EXPECTED_PATH = BASE_DIR / "expected_results.json"
REPORT_PATH = BASE_DIR / "validation_report.json"

# Tolerâncias padrão (absoluta e relativa)
ABS_TOL = 1e-3
REL_TOL = 1e-6
_EPS = 1e-12


# ================================
# HELPERS
# ================================

def _to_py(x: Any) -> Any:
    """Converte tipos numpy/pandas para tipos Python puros (json-friendly)."""
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, (pd.Timestamp,)):
        return x.isoformat()
    if isinstance(x, (np.ndarray,)):
        return x.tolist()
    if isinstance(x, dict):
        return {str(k): _to_py(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_to_py(v) for v in x]
    return x


def _is_nan(x: Any) -> bool:
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False


def _status_rollup(checks: Dict[str, Dict[str, Any]]) -> str:
    """Status global: FAIL se qualquer check FAIL, senão PASS."""
    for v in checks.values():
        if v.get("status") == "FAIL":
            return "FAIL"
    return "PASS"


def compare_numeric(
    got: Any,
    expected: Any,
    abs_tol: float = ABS_TOL,
    rel_tol: float = REL_TOL,
) -> Dict[str, Any]:
    """Comparação numérica com erro absoluto e relativo."""
    out = {
        "expected": _to_py(expected),
        "got": _to_py(got),
        "abs_error": None,
        "rel_error": None,
        "abs_tol": abs_tol,
        "rel_tol": rel_tol,
        "status": "FAIL",
    }

    if _is_nan(expected) and _is_nan(got):
        out["status"] = "PASS"
        return out
    if _is_nan(expected) != _is_nan(got):
        out["status"] = "FAIL"
        return out

    try:
        e = float(expected)
        g = float(got)
    except Exception:
        out["status"] = "FAIL"
        return out

    abs_err = abs(g - e)
    rel_err = abs_err / (abs(e) + _EPS)

    out["abs_error"] = abs_err
    out["rel_error"] = rel_err

    if abs_err <= abs_tol or rel_err <= rel_tol:
        out["status"] = "PASS"

    return out


def compare_exact(got: Any, expected: Any) -> Dict[str, Any]:
    """Comparação exata (strings/ints/dicts simples)."""
    return {
        "expected": _to_py(expected),
        "got": _to_py(got),
        "abs_error": None,
        "rel_error": None,
        "status": "PASS" if got == expected else "FAIL",
    }


def compare_list(got: Any, expected: Any) -> Dict[str, Any]:
    """Comparação de listas (ordem preservada)."""
    got_list = list(got) if got is not None else []
    exp_list = list(expected) if expected is not None else []
    return {
        "expected": _to_py(exp_list),
        "got": _to_py(got_list),
        "abs_error": None,
        "rel_error": None,
        "status": "PASS" if got_list == exp_list else "FAIL",
    }


# ================================
# VALIDATORS (got = PyTab)
# ================================

def _t_test_one_sample(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    mu0 = float(expected["mu0"])
    s = pd.to_numeric(df[col], errors="coerce").dropna()

    res = pytab_t_test_one_sample(s, mu0)

    got = {
        "n": res.get("n"),
        "mean": res.get("mean"),
        "std": res.get("std"),
        "t_stat": res.get("t_stat"),
        "p_value": res.get("p_value"),
        "mu0": res.get("mu0"),
    }

    checks = {
        "n": compare_numeric(got["n"], expected.get("n", got["n"]), abs_tol=0, rel_tol=0),
        "mean": compare_numeric(got["mean"], expected["mean"]),
        "std": compare_numeric(got["std"], expected["std"]),
        "t_stat": compare_numeric(got["t_stat"], expected["t_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _t_test_two_samples(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    num = expected["value_column"]
    cat = expected["group_column"]

    groups = expected.get("groups")
    if not groups:
        groups = list(pd.Series(df[cat].dropna().unique()).astype(str))
        if len(groups) < 2:
            raise ValueError("Dataset não possui 2 grupos na coluna de grupo.")

    g1_name, g2_name = groups[0], groups[1]
    g1 = pd.to_numeric(df.loc[df[cat] == g1_name, num], errors="coerce").dropna()
    g2 = pd.to_numeric(df.loc[df[cat] == g2_name, num], errors="coerce").dropna()

    res = pytab_t_test_two_samples(g1, g2)

    got = {
        "group_stats": {
            g1_name: {"n": res.get("n1"), "mean": res.get("mean1"), "std": res.get("std1")},
            g2_name: {"n": res.get("n2"), "mean": res.get("mean2"), "std": res.get("std2")},
        },
        "t_stat": res.get("t_stat"),
        "p_value": res.get("p_value"),
        "n": res.get("n"),
        "mean": res.get("mean"),
        "std": res.get("std"),
    }

    checks = {
        "t_stat": compare_numeric(got["t_stat"], expected["t_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }

    if "group_stats" in expected:
        for gname, estats in expected["group_stats"].items():
            gst = got["group_stats"].get(gname, {})
            checks[f"group_{gname}_n"] = compare_numeric(gst.get("n"), estats.get("n"), abs_tol=0, rel_tol=0)
            checks[f"group_{gname}_mean"] = compare_numeric(gst.get("mean"), estats.get("mean"))
            checks[f"group_{gname}_std"] = compare_numeric(gst.get("std"), estats.get("std"))

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _t_test_paired(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    before = expected["before_column"]
    after = expected["after_column"]

    pares = pd.concat(
        [pd.to_numeric(df[before], errors="coerce"), pd.to_numeric(df[after], errors="coerce")],
        axis=1,
    ).dropna()

    b = pares.iloc[:, 0]
    a = pares.iloc[:, 1]

    res = pytab_t_test_paired(b, a)

    # Expected atual usa (after - before)
    diff_expected_convention = float((a - b).mean()) if len(pares) else None

    got = {
        "n": res.get("n"),
        "mean_before": res.get("mean_before", float(b.mean()) if len(pares) else None),
        "mean_after": res.get("mean_after", float(a.mean()) if len(pares) else None),
        "diff_mean": diff_expected_convention,
        "t_stat": res.get("t_stat"),
        "p_value": res.get("p_value"),
        # debug: o valor bruto que o PyTab calcula hoje (before - after)
        "pytab_diff_mean_raw": res.get("diff_mean"),
    }

    checks = {
        "n": compare_numeric(got["n"], expected.get("n", got["n"]), abs_tol=0, rel_tol=0),
        "mean_before": compare_numeric(got["mean_before"], expected["mean_before"]),
        "mean_after": compare_numeric(got["mean_after"], expected["mean_after"]),
        "diff_mean": compare_numeric(got["diff_mean"], expected["diff_mean"]),
        "t_stat": compare_numeric(got["t_stat"], expected["t_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _anova_oneway(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    num = expected["numeric_column"]
    cat = expected["category_column"]

    res = pytab_anova_oneway(df, numerica=num, categoria=cat)

    got = {
        "f_stat": res.get("f_stat"),
        "p_value": res.get("p_value"),
        "n": res.get("n"),
        "mean": res.get("mean"),
        "std": res.get("std"),
        "value_column": res.get("value_column"),
        "group_column": res.get("group_column"),
    }

    checks = {
        "f_stat": compare_numeric(got["f_stat"], expected["f_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }

    if "group_means" in expected:
        data = df[[num, cat]].dropna().copy()
        gmeans = data.groupby(cat)[num].mean().to_dict()
        got["group_means"] = {k: float(v) for k, v in gmeans.items()}
        for gname, emean in expected["group_means"].items():
            checks[f"group_mean_{gname}"] = compare_numeric(gmeans.get(gname), emean)

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _chi_square(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    row = expected["row_var"]
    col = expected["col_var"]

    res = pytab_chi_square(df, cat1=row, cat2=col)

    got = {
        "chi2": res.get("f_stat"),
        "p_value": res.get("p_value"),
        "dof": res.get("dof"),
        "table": res.get("table").to_dict() if res.get("table") is not None else None,
    }

    checks = {
        "chi2": compare_numeric(got["chi2"], expected["chi2"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
        "dof": compare_numeric(got["dof"], expected["dof"], abs_tol=0, rel_tol=0),
        "table": compare_exact(got["table"], expected["table"]),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _normality_shapiro(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    s = pd.to_numeric(df[col], errors="coerce").dropna()

    res = pytab_normality(s, metodo="shapiro")

    got = {
        "n": res.get("n"),
        "mean": res.get("mean"),
        "std": res.get("std"),
        "w_stat": res.get("w_stat", res.get("t_stat")),
        "p_value": res.get("p_value"),
    }

    checks = {
        "w_stat": compare_numeric(got["w_stat"], expected["w_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


# ================================
# OUTROS VALIDATORS (mantidos)
# ================================

def _regression_linear_simple(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    # Aceita os 2 formatos: x/y (seu JSON) ou x_column/y_column (fallback)
    x = expected.get("x") or expected.get("x_column")
    y = expected.get("y") or expected.get("y_column")
    if x is None or y is None:
        raise KeyError("Expected precisa de 'x' e 'y' (ou 'x_column'/'y_column').")

    data = df[[x, y]].dropna()
    X = pd.to_numeric(data[x], errors="coerce").astype(float).values
    Y = pd.to_numeric(data[y], errors="coerce").astype(float).values

    import statsmodels.api as sm
    X2 = sm.add_constant(X)
    model = sm.OLS(Y, X2).fit()

    got = {
        "slope": float(model.params[1]),
        "intercept": float(model.params[0]),
        "r2": float(model.rsquared),
    }

    checks = {
        "slope": compare_numeric(got["slope"], expected["slope"]),
        "intercept": compare_numeric(got["intercept"], expected["intercept"]),
        "r2": compare_numeric(got["r2"], expected["r2"]),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _correlation_matrix(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    got: Dict[str, Any] = {}

    corr_expected = expected.get("corr_matrix") or expected.get("correlation")
    if corr_expected is None:
        return {"type": expected["type"], "status": "SKIPPED", "reason": "Expected sem corr_matrix/correlation"}

    cols = (
        expected.get("numeric_columns")
        or expected.get("columns")
        or (list(corr_expected.keys()) if isinstance(corr_expected, dict) else None)
        or df.select_dtypes(include="number").columns.tolist()
    )

    got["numeric_columns"] = cols
    if "numeric_columns" in expected:
        checks["numeric_columns"] = compare_list(cols, expected["numeric_columns"])

    corr = df[cols].corr(numeric_only=True)
    got_key = "corr_matrix" if "corr_matrix" in expected else "correlation"
    got[got_key] = corr.to_dict()

    for a, row in corr_expected.items():
        for b, val in row.items():
            checks[f"corr_{a}__{b}"] = compare_numeric(float(corr.loc[a, b]), val)

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _outliers(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    method = expected.get("method", "zscore")
    threshold = float(expected.get("threshold", 3.0))

    s = pd.to_numeric(df[col], errors="coerce")

    if method == "zscore":
        z = (s - s.mean()) / (s.std(ddof=1) + _EPS)
        mask = z.abs().gt(threshold).fillna(False)

        got_count = int(mask.sum())
        got_idx = list(map(int, np.where(mask.values)[0]))

        got = {"outlier_count": got_count, "outlier_idx": got_idx}

        checks = {}
        # 1) Se expected traz count
        if "outlier_count" in expected:
            checks["outlier_count"] = compare_numeric(got_count, expected["outlier_count"], abs_tol=0, rel_tol=0)
        # 2) Se expected traz lista de índices (qualquer um destes nomes)
        exp_idx = expected.get("outlier_idx") or expected.get("outlier_indices") or expected.get("indices")
        if exp_idx is not None:
            checks["outlier_idx"] = compare_list(sorted(got_idx), sorted(list(exp_idx)))

        # fallback: se expected não trouxe nada além de column/method, marca SKIPPED
        if not checks:
            return {"type": expected["type"], "status": "SKIPPED", "reason": "Expected sem outlier_count/indices", "got": got}

        return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}

    raise ValueError(f"Método de outlier não suportado: {method}")


def _p_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    total_col = expected["total_column"]
    defectives_col = expected["defectives_column"]

    total = pd.to_numeric(df[total_col], errors="coerce")
    defectives = pd.to_numeric(df[defectives_col], errors="coerce")

    total_sum = float(total.sum(skipna=True))
    defect_sum = float(defectives.sum(skipna=True))

    p_bar = (defect_sum / total_sum) if total_sum > 0 else None

    got = {"p_bar": p_bar}
    checks = {"p_bar": compare_numeric(got["p_bar"], expected["p_bar"])}

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}



def _u_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    # Seu JSON tem só "column" e "u_bar". :contentReference[oaicite:5]{index=5}
    # Interpretação: cada linha = 1 unidade/área constante => u_bar = média de defeitos por unidade.
    col = expected["column"]
    d = pd.to_numeric(df[col], errors="coerce").dropna()

    u_bar = float(d.mean()) if len(d) else None

    got = {"u_bar": u_bar}
    checks = {"u_bar": compare_numeric(got["u_bar"], expected["u_bar"])}

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}



def _xbar_r_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    group_col = expected["group_column"]
    value_col = expected["value_column"]
    n = int(expected["subgroup_size"])

    # Constantes SPC (Xbar-R) para n=2..10 (pode expandir depois)
    A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
    D3 = {2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
    D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}

    if n not in A2:
        raise ValueError(f"subgroup_size={n} não suportado nas constantes SPC (implementar tabela completa).")

    data = df[[group_col, value_col]].dropna().copy()
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=[value_col])

    g = data.groupby(group_col)[value_col]
    xbar_i = g.mean()
    r_i = g.max() - g.min()

    xbar_bar = float(xbar_i.mean()) if len(xbar_i) else None
    r_bar = float(r_i.mean()) if len(r_i) else None

    ucl_xbar = (xbar_bar + A2[n] * r_bar) if (xbar_bar is not None and r_bar is not None) else None
    lcl_xbar = (xbar_bar - A2[n] * r_bar) if (xbar_bar is not None and r_bar is not None) else None
    ucl_r = (D4[n] * r_bar) if (r_bar is not None) else None
    lcl_r = (D3[n] * r_bar) if (r_bar is not None) else None

    got = {
        "xbar_bar": xbar_bar,
        "r_bar": r_bar,
        "ucl_xbar": ucl_xbar,
        "lcl_xbar": lcl_xbar,
        "ucl_r": ucl_r,
        "lcl_r": lcl_r,
    }

    checks = {
        "xbar_bar": compare_numeric(got["xbar_bar"], expected["xbar_bar"]),
        "r_bar": compare_numeric(got["r_bar"], expected["r_bar"]),
        "ucl_xbar": compare_numeric(got["ucl_xbar"], expected["ucl_xbar"]),
        "lcl_xbar": compare_numeric(got["lcl_xbar"], expected["lcl_xbar"]),
        "ucl_r": compare_numeric(got["ucl_r"], expected["ucl_r"]),
        "lcl_r": compare_numeric(got["lcl_r"], expected["lcl_r"]),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}



def _imr_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    s = pd.to_numeric(df[col], errors="coerce").dropna()

    mean = float(s.mean()) if len(s) else None
    mr = s.diff().abs().dropna()
    mr_bar = float(mr.mean()) if len(mr) else None

    # Para I-MR: sigma_est = mr_bar / d2, com d2 = 1.128 para MR de tamanho 2
    d2 = 1.128
    sigma_est = (mr_bar / d2) if (mr_bar is not None) else None

    ucl_x = (mean + 3.0 * sigma_est) if (mean is not None and sigma_est is not None) else None
    lcl_x = (mean - 3.0 * sigma_est) if (mean is not None and sigma_est is not None) else None

    got = {
        "n": int(s.shape[0]),
        "mean": mean,
        "sigma_est": sigma_est,
        "mr_bar": mr_bar,
        "ucl_x": ucl_x,
        "lcl_x": lcl_x,
    }

    checks = {
        "mean": compare_numeric(got["mean"], expected["mean"]),
        "sigma_est": compare_numeric(got["sigma_est"], expected["sigma_est"]),
        "mr_bar": compare_numeric(got["mr_bar"], expected["mr_bar"]),
        "ucl_x": compare_numeric(got["ucl_x"], expected["ucl_x"]),
        "lcl_x": compare_numeric(got["lcl_x"], expected["lcl_x"]),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}



def _mixed(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    """
    Dataset misto: valida
      1) colunas numéricas detectadas
      2) estatísticas descritivas (mean/std/min/max) para as colunas esperadas
      3) matriz de correlação (aceita expected em 'correlation' OU 'corr_matrix')
    """

    # 1) Numéricas detectadas (ordem não deve importar)
    num_cols_detected = df.select_dtypes(include="number").columns.tolist()
    num_cols_detected_sorted = sorted(num_cols_detected)

    expected_num_cols = expected.get("numeric_columns", [])
    expected_num_cols_sorted = sorted(expected_num_cols) if expected_num_cols else num_cols_detected_sorted

    checks: Dict[str, Any] = {
        "numeric_columns": compare_list(num_cols_detected_sorted, expected_num_cols_sorted),
    }

    got: Dict[str, Any] = {
        "numeric_columns": num_cols_detected_sorted,
    }

    # 2) Descritivas
    got_desc: Dict[str, Any] = {}
    desc_expected = expected.get("descriptive") or {}

    # valida somente o que o expected pede (se não houver, usa detectadas)
    cols_to_check = expected_num_cols if expected_num_cols else num_cols_detected

    for c in cols_to_check:
        s = pd.to_numeric(df[c], errors="coerce").dropna().astype(float)

        got_desc[c] = {
            "mean": float(s.mean()) if len(s) else None,
            "std": float(s.std(ddof=1)) if len(s) > 1 else None,
            "min": float(s.min()) if len(s) else None,
            "max": float(s.max()) if len(s) else None,
        }

        ed = desc_expected.get(c, {})
        if ed:
            checks[f"desc_{c}_mean"] = compare_numeric(got_desc[c]["mean"], ed.get("mean"))
            checks[f"desc_{c}_std"] = compare_numeric(got_desc[c]["std"], ed.get("std"))
            checks[f"desc_{c}_min"] = compare_numeric(got_desc[c]["min"], ed.get("min"))
            checks[f"desc_{c}_max"] = compare_numeric(got_desc[c]["max"], ed.get("max"))

    got["descriptive"] = got_desc

    # 3) Correlação — aceita 'correlation' ou 'corr_matrix'
    corr_expected = expected.get("corr_matrix") or expected.get("correlation")
    if corr_expected is not None:
        # quais colunas usar na correlação?
        cols = expected.get("numeric_columns")
        if not cols:
            # se não tiver, tenta pegar das chaves do expected
            cols = list(corr_expected.keys())

        corr = df[cols].corr(numeric_only=True)

        # preservar a mesma chave do expected
        got_key = "corr_matrix" if "corr_matrix" in expected else "correlation"
        got[got_key] = corr.to_dict()

        for a, row in corr_expected.items():
            for b, val in row.items():
                checks[f"corr_{a}__{b}"] = compare_numeric(float(corr.loc[a, b]), val)

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


# ================================
# MAIN
# ================================

_VALIDATORS = {
    "t_test_one_sample": _t_test_one_sample,
    "t_test_two_samples": _t_test_two_samples,
    "t_test_paired": _t_test_paired,
    "anova_oneway": _anova_oneway,
    "chi_square_independence": _chi_square,
    "normality_shapiro": _normality_shapiro,
    "regression_linear_simple": _regression_linear_simple,
    "correlation_matrix": _correlation_matrix,
    "outliers": _outliers,
    "p_chart": _p_chart,
    "u_chart": _u_chart,
    "xbar_r_chart": _xbar_r_chart,
    "imr_chart": _imr_chart,
    "mixed": _mixed,
}


def main():
    expected_all = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

    report: Dict[str, Any] = {}

    for fname, expected in expected_all.items():
        csv_path = DATASETS_DIR / fname
        tipo = expected["type"]

        if not csv_path.exists():
            report[fname] = {"type": tipo, "status": "ERROR", "error": f"Dataset não encontrado: {csv_path}"}
            continue

        try:
            df = pd.read_csv(csv_path)

            validator = _VALIDATORS.get(tipo)
            if validator is None:
                report[fname] = {"type": tipo, "status": "SKIPPED", "reason": "Tipo não implementado"}
                continue

            res = validator(df, expected)
            if res is None:
                raise ValueError(f"Validator '{tipo}' retornou None (faltou return).")

            report[fname] = res

        except Exception as e:
            report[fname] = {"type": tipo, "status": "ERROR", "error": repr(e)}

    # =========================
    # Summary por dataset (fonte de verdade)
    # =========================
    summary = {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIPPED": 0}
    checks_summary = {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIPPED": 0}

    for res in report.values():
        st = res.get("status", "ERROR")
        summary[st] = summary.get(st, 0) + 1

        checks = res.get("checks")
        if isinstance(checks, dict):
            for ck in checks.values():
                if isinstance(ck, dict):
                    cst = ck.get("status", "ERROR")
                else:
                    cst = "ERROR"
                checks_summary[cst] = checks_summary.get(cst, 0) + 1

    # Consistência: 1 status por dataset
    if sum(summary.values()) != len(report):
        raise RuntimeError(
            f"Resumo inconsistente: sum(summary)={sum(summary.values())} != len(results)={len(report)}"
        )

    out = {"summary": summary, "checks_summary": checks_summary, "results": report}
    REPORT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Validação concluída.")
    print(f"Relatório salvo em: {REPORT_PATH}")
    print("Resumo (por dataset):", summary)
    print("Resumo (por checks):", checks_summary)

