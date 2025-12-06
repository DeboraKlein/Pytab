# PyTab module initializer
from .descriptive import summarize_numeric
from .outliers import (
    zscore_series,
    detect_outliers_zscore,
    detect_outliers_iqr,
    detect_outliers,
)

__all__ = [
    "summarize_numeric",
    "zscore_series",
    "detect_outliers_zscore",
    "detect_outliers_iqr",
    "detect_outliers",
]
