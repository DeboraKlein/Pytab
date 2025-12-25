import json
import math
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd


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
# HELPERS (comparação + serialização)
# ================================

def _to_py(x: Any) -> Any:
    """Converte tipos numpy/pandas para tipos JSON-friendly."""
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, pd.Series):
        return x.tolist()
    if isinstance(x, pd.DataFrame):
        return x.to_dict()
    return x


def _is_nan(x: Any) -> bool:
    try:
        return (
            x is None
            or (isinstance(x, float) and math.isnan(x))
            or (isinstance(x, np.floating) and np.isnan(x))
        )
    except Exception:
        return False


def compare_numeric(
    got: Any,
    expected: Any,
    abs_tol: float = ABS_TOL,
    rel_tol: float = REL_TOL,
) -> Dict[str, Any]:
    """Compara números (suporta None/NaN) e retorna bloco autoexplicativo."""
    out: Dict[str, Any] = {
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
    rel_err = abs_err / max(abs(e), _EPS)

    out["abs_error"] = abs_err
    out["rel_error"] = rel_err
    out["status"] = "PASS" if (abs_err <= abs_tol or rel_err <= rel_tol) else "FAIL"
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
    got_list = list(got) if got is not None else None
    exp_list = list(expected) if expected is not None else None

    status = "PASS" if got_list == exp_list else "FAIL"
    details = {}
    if status == "FAIL" and got_list is not None and exp_list is not None:
        exp_set = set(exp_list)
        got_set = set(got_list)
        details = {
            "missing": sorted(list(exp_set - got_set)),
            "extra": sorted(list(got_set - exp_set)),
        }

    return {
        "expected": _to_py(exp_list),
        "got": _to_py(got_list),
        "abs_error": None,
        "rel_error": None,
        "status": status,
        **({"details": details} if details else {}),
    }


def _status_rollup(checks: Dict[str, Any]) -> str:
    statuses = [v.get("status") for v in checks.values() if isinstance(v, dict)]
    if not statuses:
        return "SKIPPED"
    if any(s == "FAIL" for s in statuses):
        return "FAIL"
    if any(s == "ERROR" for s in statuses):
        return "ERROR"
    return "PASS"


# ================================
# VALIDATORS (referência)
# ================================

def _t_test_one_sample(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    mu0 = float(expected["mu0"])
    s = pd.to_numeric(df[col], errors="coerce").dropna()

    n = int(s.shape[0])
    mean = float(s.mean()) if n else None
    std = float(s.std(ddof=1)) if n > 1 else None

    t_stat = p_value = None
    if n >= 2:
        import scipy.stats as stats
        t_stat, p_value = stats.ttest_1samp(s, popmean=mu0)

    got = {
        "n": n,
        "mean": mean,
        "std": std,
        "t_stat": None if _is_nan(t_stat) else float(t_stat),
        "p_value": None if _is_nan(p_value) else float(p_value),
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

    import scipy.stats as stats
    t_stat = p_value = None
    if len(g1) >= 2 and len(g2) >= 2:
        t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)  # Welch

    got = {
        "group_stats": {
            g1_name: {
                "n": int(len(g1)),
                "mean": float(g1.mean()) if len(g1) else None,
                "std": float(g1.std(ddof=1)) if len(g1) > 1 else None,
            },
            g2_name: {
                "n": int(len(g2)),
                "mean": float(g2.mean()) if len(g2) else None,
                "std": float(g2.std(ddof=1)) if len(g2) > 1 else None,
            },
        },
        "t_stat": None if _is_nan(t_stat) else float(t_stat),
        "p_value": None if _is_nan(p_value) else float(p_value),
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

    n = int(len(pares))
    mean_before = float(b.mean()) if n else None
    mean_after = float(a.mean()) if n else None
    diff_mean = float((a - b).mean()) if n else None

    import scipy.stats as stats
    t_stat = p_value = None
    if n >= 2:
        t_stat, p_value = stats.ttest_rel(b, a)

    got = {
        "n": n,
        "mean_before": mean_before,
        "mean_after": mean_after,
        "diff_mean": diff_mean,
        "t_stat": None if _is_nan(t_stat) else float(t_stat),
        "p_value": None if _is_nan(p_value) else float(p_value),
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

    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    data = df[[num, cat]].dropna().copy()
    data = data.rename(columns={num: "__y__", cat: "__g__"})
    if data["__g__"].nunique(dropna=True) < 2:
        raise ValueError("ANOVA one-way exige pelo menos 2 grupos.")

    model = smf.ols("__y__ ~ C(__g__)", data=data).fit()
    table = sm.stats.anova_lm(model, typ=2)

    got = {
        "f_stat": float(table["F"].iloc[0]),
        "p_value": float(table["PR(>F)"].iloc[0]),
    }

    checks = {
        "f_stat": compare_numeric(got["f_stat"], expected["f_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }

    if "group_means" in expected:
        gmeans = data.groupby("__g__")["__y__"].mean().to_dict()
        got["group_means"] = {k: float(v) for k, v in gmeans.items()}
        for gname, emean in expected["group_means"].items():
            checks[f"group_mean_{gname}"] = compare_numeric(gmeans.get(gname), emean)

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _chi_square(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    row = expected["row_var"]
    col = expected["col_var"]

    import scipy.stats as stats
    table = pd.crosstab(df[row], df[col])
    chi2, p_value, dof, _ = stats.chi2_contingency(table)

    got = {
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "table": table.to_dict(),
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

    import scipy.stats as stats
    w_stat = p_value = None
    if len(s) >= 3:
        w_stat, p_value = stats.shapiro(s)

    got = {
        "w_stat": None if _is_nan(w_stat) else float(w_stat),
        "p_value": None if _is_nan(p_value) else float(p_value),
    }

    checks = {
        "w_stat": compare_numeric(got["w_stat"], expected["w_stat"]),
        "p_value": compare_numeric(got["p_value"], expected["p_value"], abs_tol=1e-6, rel_tol=1e-3),
    }
    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _regression_linear_simple(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    x = pd.to_numeric(df[expected["x"]], errors="coerce")
    y = pd.to_numeric(df[expected["y"]], errors="coerce")
    data = pd.concat([x, y], axis=1).dropna()

    import scipy.stats as stats
    lr = stats.linregress(data.iloc[:, 0].astype(float), data.iloc[:, 1].astype(float))

    got = {
        "slope": float(lr.slope),
        "intercept": float(lr.intercept),
        "r2": float(lr.rvalue ** 2),
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

    # Aceita "correlation" ou "corr_matrix" no expected
    corr_expected = expected.get("corr_matrix") or expected.get("correlation")
    if corr_expected is None:
        return {
            "type": expected["type"],
            "status": "SKIPPED",
            "reason": "Expected sem corr_matrix/correlation",
        }

    # Descobre colunas: 1) numeric_columns 2) columns 3) chaves da matriz 4) inferência por dtype
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

    # Salva no got com o mesmo nome do expected
    got_key = "corr_matrix" if "corr_matrix" in expected else "correlation"
    got[got_key] = corr.to_dict()

    # Compara coeficientes esperados
    for a, row in corr_expected.items():
        for b, val in row.items():
            checks[f"corr_{a}__{b}"] = compare_numeric(float(corr.loc[a, b]), val)

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}



def _outliers(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    s = pd.to_numeric(df[col], errors="coerce")

    mean = float(s.mean())
    std = float(s.std(ddof=1))
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = float(q3 - q1)
    lower = float(q1 - 1.5 * iqr)
    upper = float(q3 + 1.5 * iqr)

    med = float(s.median())
    mad = float((s - med).abs().median())

    zthr = float(expected.get("zscore_threshold", 3.0))
    z = (s - mean) / (std if std != 0 else np.nan)

    z_idx = s.index[(z.abs() > zthr) & z.notna()].tolist()
    iqr_idx = s.index[((s < lower) | (s > upper)) & s.notna()].tolist()

    got = {
        "mean": mean,
        "std": std,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_iqr_bound": lower,
        "upper_iqr_bound": upper,
        "mad": mad,
        "zscore_threshold": zthr,
        "zscore_outlier_indices": [int(i) for i in z_idx],
        "iqr_outlier_indices": [int(i) for i in iqr_idx],
    }

    checks = {
        "mean": compare_numeric(got["mean"], expected["mean"]),
        "std": compare_numeric(got["std"], expected["std"]),
        "q1": compare_numeric(got["q1"], expected["q1"]),
        "q3": compare_numeric(got["q3"], expected["q3"]),
        "iqr": compare_numeric(got["iqr"], expected["iqr"]),
        "lower_iqr_bound": compare_numeric(got["lower_iqr_bound"], expected["lower_iqr_bound"]),
        "upper_iqr_bound": compare_numeric(got["upper_iqr_bound"], expected["upper_iqr_bound"]),
        "mad": compare_numeric(got["mad"], expected["mad"]),
        "zscore_outlier_indices": compare_list(got["zscore_outlier_indices"], expected["zscore_outlier_indices"]),
        "iqr_outlier_indices": compare_list(got["iqr_outlier_indices"], expected["iqr_outlier_indices"]),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _p_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    total_col = expected["total_column"]
    def_col = expected["defectives_column"]

    total = pd.to_numeric(df[total_col], errors="coerce").dropna()
    defs = pd.to_numeric(df[def_col], errors="coerce").dropna()

    got = {"p_bar": float(defs.sum() / total.sum())}
    checks = {"p_bar": compare_numeric(got["p_bar"], expected["p_bar"])}

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _u_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    col = expected["column"]
    s = pd.to_numeric(df[col], errors="coerce").dropna()

    got = {"u_bar": float(s.mean())}
    checks = {"u_bar": compare_numeric(got["u_bar"], expected["u_bar"])}

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _xbar_r_chart(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    group_col = expected["group_column"]
    value_col = expected["value_column"]
    n = int(expected["subgroup_size"])

    data = df[[group_col, value_col]].dropna().copy()
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=[value_col])

    grp = data.groupby(group_col)[value_col]
    xbars = grp.mean()
    rs = grp.max() - grp.min()

    xbar_bar = float(xbars.mean())
    r_bar = float(rs.mean())

    A2 = {2: 1.88, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483}
    D3 = {2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}
    D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004}

    got = {
        "xbar_bar": xbar_bar,
        "r_bar": r_bar,
        "ucl_xbar": float(xbar_bar + A2[n] * r_bar),
        "lcl_xbar": float(xbar_bar - A2[n] * r_bar),
        "ucl_r": float(D4[n] * r_bar),
        "lcl_r": float(D3[n] * r_bar),
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
    s = pd.to_numeric(df[col], errors="coerce").dropna().astype(float)

    n = int(len(s))
    mean = float(s.mean())
    mr = (s.diff().abs()).dropna()
    mr_bar = float(mr.mean()) if len(mr) else 0.0

    d2 = 1.128  # n=2
    sigma_est = float(mr_bar / d2) if mr_bar > 0 else 0.0

    got = {
        "n": n,
        "mean": mean,
        "mr_bar": mr_bar,
        "sigma_est": sigma_est,
        "ucl_x": float(mean + 3 * sigma_est),
        "lcl_x": float(mean - 3 * sigma_est),
    }

    checks = {
        "n": compare_numeric(got["n"], expected.get("n", got["n"]), abs_tol=0, rel_tol=0),
        "mean": compare_numeric(got["mean"], expected["mean"]),
        "mr_bar": compare_numeric(got["mr_bar"], expected["mr_bar"]),
        "sigma_est": compare_numeric(got["sigma_est"], expected["sigma_est"]),
        "ucl_x": compare_numeric(got["ucl_x"], expected["ucl_x"]),
        "lcl_x": compare_numeric(got["lcl_x"], expected["lcl_x"]),
    }

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


def _mixed(df: pd.DataFrame, expected: dict) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    got: Dict[str, Any] = {}

    # 1) Colunas numéricas detectadas
    num_cols = df.select_dtypes(include="number").columns.tolist()
    got["numeric_columns"] = num_cols

    if "numeric_columns" in expected:
        checks["numeric_columns"] = compare_list(num_cols, expected["numeric_columns"])

    # 2) Descritivas (usa as colunas declaradas no expected, para ficar determinístico)
    exp_desc = expected.get("descriptive") or {}
    got_desc: Dict[str, Any] = {}

    for c, ed in exp_desc.items():
        s = pd.to_numeric(df[c], errors="coerce").dropna()

        got_desc[c] = {
            "mean": float(s.mean()) if len(s) else None,
            "std": float(s.std(ddof=1)) if len(s) > 1 else None,
            "min": float(s.min()) if len(s) else None,
            "max": float(s.max()) if len(s) else None,
        }

        checks[f"desc_{c}_mean"] = compare_numeric(got_desc[c]["mean"], ed.get("mean"))
        checks[f"desc_{c}_std"] = compare_numeric(got_desc[c]["std"], ed.get("std"))
        checks[f"desc_{c}_min"] = compare_numeric(got_desc[c]["min"], ed.get("min"))
        checks[f"desc_{c}_max"] = compare_numeric(got_desc[c]["max"], ed.get("max"))

    got["descriptive"] = got_desc

    # 3) Correlação (aceita 'correlation' ou 'corr_matrix')
    corr_expected = expected.get("corr_matrix") or expected.get("correlation")
    if corr_expected is not None:
        cols = expected.get("numeric_columns") or list(corr_expected.keys())
        corr = df[cols].corr(numeric_only=True)

        got_key = "corr_matrix" if "corr_matrix" in expected else "correlation"
        got[got_key] = corr.to_dict()

        for a, row in corr_expected.items():
            for b, val in row.items():
                checks[f"corr_{a}__{b}"] = compare_numeric(float(corr.loc[a, b]), val)

    return {"type": expected["type"], "status": _status_rollup(checks), "checks": checks, "got": got}


    corr_expected = expected.get("corr_matrix") or expected.get("correlation")
    if corr_expected is not None:
        corr = df[expected["numeric_columns"]].corr(numeric_only=True)

        got_key = "corr_matrix" if "corr_matrix" in expected else "correlation"
        got[got_key] = corr.to_dict()

        for a, row in corr_expected.items():
            for b, val in row.items():
                checks[f"corr_{a}__{b}"] = compare_numeric(float(corr.loc[a, b]), val)


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
    summary = {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIPPED": 0}

    for fname, expected in expected_all.items():
        csv_path = DATASETS_DIR / fname
        tipo = expected["type"]

        if not csv_path.exists():
            report[fname] = {"type": tipo, "status": "ERROR", "error": f"Dataset não encontrado: {csv_path}"}
            summary["ERROR"] += 1
            continue

        try:
            df = pd.read_csv(csv_path)

            validator = _VALIDATORS.get(tipo)
            if validator is None:
                report[fname] = {"type": tipo, "status": "SKIPPED", "reason": "Tipo não implementado"}
                summary["SKIPPED"] += 1
                continue

            res = validator(df, expected)
            report[fname] = res
            summary[res["status"]] = summary.get(res["status"], 0) + 1
            if res is None:
                raise ValueError(f"Validator '{tipo}' retornou None (faltou return).")


        except Exception as e:
            report[fname] = {"type": tipo, "status": "ERROR", "error": repr(e)}
            summary["ERROR"] += 1

    out = {"summary": summary, "results": report}
    REPORT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Validação concluída.")
    print(f"Relatório salvo em: {REPORT_PATH}")
    print("Resumo:", summary)


if __name__ == "__main__":
    main()


