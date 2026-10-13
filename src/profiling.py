"""Data-profiling helpers for the EDA pages (pure functions, no Streamlit)."""
import numpy as np
import pandas as pd

from src.config import FLAG_COLUMNS, ID_LIKE, NOT_REJECTED


def numeric_columns(df: pd.DataFrame, include_flags: bool = False) -> list:
    """Continuous-looking numeric columns (IDs, calendar parts and, by default, 0/1 flags removed)."""
    skip = set(ID_LIKE) | (set() if include_flags else set(FLAG_COLUMNS))
    return [c for c in df.columns
            if pd.api.types.is_numeric_dtype(df[c]) and c not in skip]


def categorical_columns(df: pd.DataFrame, max_levels: int = 30) -> list:
    """Text columns with a manageable number of levels (so charts stay readable)."""
    return [c for c in df.columns
            if c not in ID_LIKE
            and not pd.api.types.is_numeric_dtype(df[c])
            and not pd.api.types.is_datetime64_any_dtype(df[c])
            and 1 < df[c].nunique() <= max_levels]


def schema_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: type, non-null count, distinct values, an example."""
    rows = []
    for col in df.columns:
        s = df[col]
        kind = ("Date" if pd.api.types.is_datetime64_any_dtype(s)
                else "Number" if pd.api.types.is_numeric_dtype(s) else "Text")
        example = s.dropna().iloc[0] if s.notna().any() else ""
        if kind == "Date":
            example = pd.Timestamp(example).date()
        rows.append({"Column": col, "Type": kind, "Non-null": int(s.notna().sum()),
                     "Distinct": int(s.nunique()), "Example": str(example)})
    return pd.DataFrame(rows)


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Blank cells per column. `Not rejected` in rejection_reason is a blank we filled on load,
    so it is counted as missing but labelled as expected."""
    rows = []
    for col in df.columns:
        blanks = int(df[col].isna().sum())
        if col == "rejection_reason":
            blanks += int((df[col] == NOT_REJECTED).sum())
        if blanks:
            rows.append({"Column": col, "Missing": blanks, "Missing %": blanks / len(df),
                         "Why": "Expected: accepted orders have no rejection reason"
                         if col == "rejection_reason" else "Needs checking"})
    return pd.DataFrame(rows, columns=["Column", "Missing", "Missing %", "Why"])


def describe_numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    d = df[cols].describe().T
    d["skew"] = df[cols].skew()
    d["kurtosis"] = df[cols].kurt()
    return d.rename(columns={"50%": "median", "25%": "q1", "75%": "q3"}).reset_index(names="Column")


def iqr_outliers(s: pd.Series) -> dict:
    """Tukey fences: a value is an outlier if it lies beyond 1.5 x IQR from the quartiles."""
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = int(((s < low) | (s > high)).sum())
    return {"low_fence": low, "high_fence": high, "outliers": flagged,
            "outlier_pct": flagged / len(s) if len(s) else 0.0}


def outlier_table(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    rows = [{"Column": c, **iqr_outliers(df[c])} for c in cols]
    return (pd.DataFrame(rows).sort_values("outlier_pct", ascending=False).reset_index(drop=True))


def top_correlations(df: pd.DataFrame, cols: list, n: int = 10) -> pd.DataFrame:
    """Strongest pairwise correlations (each pair listed once)."""
    corr = df[cols].corr()
    pairs = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1)).stack().dropna().reset_index()
    pairs.columns = ["Variable A", "Variable B", "Correlation"]
    order = pairs["Correlation"].abs().sort_values(ascending=False).index
    return pairs.loc[order].head(n).reset_index(drop=True)


def category_summary(df: pd.DataFrame, col: str) -> pd.DataFrame:
    counts = df[col].value_counts()
    return pd.DataFrame({col: counts.index, "Orders": counts.values,
                         "Share": counts.values / counts.sum()})
