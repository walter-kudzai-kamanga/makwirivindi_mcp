from pathlib import Path
import pandas as pd
import numpy as np

UPLOAD_DIR = Path("uploads")

CSV_EXT = {".csv"}
EXCEL_EXT = {".xlsx", ".xls"}


def _read_file(path: Path):
    """Load a CSV or Excel file (all sheets) into a list of (name, df)."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in CSV_EXT:
        return [("data", pd.read_csv(path))]
    if suffix in EXCEL_EXT:
        try:
            xl = pd.ExcelFile(path, engine="openpyxl" if suffix == ".xlsx" else None)
            return [(name, pd.read_excel(xl, sheet_name=name)) for name in xl.sheet_names]
        except Exception:
            return [("Sheet1", pd.read_excel(path))]
    return []


def _detect_date_column(df: pd.DataFrame):
    """Return first column that looks like datetime."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
        try:
            if df[col].dropna().empty:
                continue
            pd.to_datetime(df[col], errors="coerce")
            if df[col].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}|^\d{2}/\d{2}/\d{4}").any():
                return col
        except Exception:
            pass
    return None


def _detect_geo_columns(df: pd.DataFrame):
    lat_col = lon_col = country_col = None
    cols_lower = {c.lower(): c for c in df.columns}
    for name, col in cols_lower.items():
        if name in ("lat", "latitude", "latitud"):
            lat_col = col
        if name in ("lon", "lng", "longitude", "longitud", "long"):
            lon_col = col
        if name in ("country", "countries", "region", "state"):
            country_col = col
    return lat_col, lon_col, country_col


def _safe_serialize(obj):
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if hasattr(obj, "item"):
        return obj.item()
    if isinstance(obj, (pd.Timestamp,)):
        return str(obj)
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj) if np.isfinite(obj) else None
    return obj


def _top_correlations(df: pd.DataFrame, n: int = 5):
    """Top N absolute correlations between numeric columns (excluding self)."""
    num = df.select_dtypes(include=["number"])
    if num.shape[1] < 2:
        return []
    corr = num.corr()
    out = []
    for i, c1 in enumerate(corr.columns):
        for j, c2 in enumerate(corr.columns):
            if i >= j:
                continue
            v = corr.iloc[i, j]
            if pd.notna(v) and abs(v) < 1.0:
                out.append({"col1": c1, "col2": c2, "value": round(float(v), 3)})
    out.sort(key=lambda x: -abs(x["value"]))
    return out[:n]


def _outlier_columns(df: pd.DataFrame):
    """Columns with potential outliers (IQR method, count of outliers)."""
    num = df.select_dtypes(include=["number"])
    out = []
    for col in num.columns:
        q1, q3 = num[col].quantile(0.25), num[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n = ((num[col] < low) | (num[col] > high)).sum()
        if n > 0:
            out.append({"column": col, "outlier_count": int(n)})
    return out


def analyze_dataset(path, sheet_name=None):
    """
    Analyze a CSV or Excel file (optionally one sheet).
    Returns dict with metadata, chart-ready data, KPIs (missing %, duplicates, correlations, preview).
    """
    path = Path(path)
    sheets = _read_file(path)
    if not sheets:
        return None
    if sheet_name is not None:
        sheets = [(n, d) for n, d in sheets if n == sheet_name]
    if not sheets:
        return None

    name, df = sheets[0]
    df = df.dropna(how="all").reset_index(drop=True)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # KPIs: missing %, duplicates, anomaly
    total_cells = df.size if df.size else 1
    missing_count = int(df.isna().sum().sum())
    missing_pct = round(100.0 * missing_count / total_cells, 1)
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round(100.0 * duplicate_rows / len(df), 1) if len(df) else 0
    correlations = _top_correlations(df, 5)
    outliers = _outlier_columns(df)
    missing_by_col = {str(c): round(100.0 * df[c].isna().sum() / len(df), 1) for c in df.columns} if len(df) else {}
    anomaly = missing_pct > 10 or duplicate_pct > 5 or len(outliers) > 0

    # Preview (first 20 rows, JSON-serializable)
    preview = df.head(20).fillna("").astype(str).to_dict(orient="records")

    # Line chart data
    line_labels, line_values = [], []
    date_col = _detect_date_column(df)
    if date_col and numeric_cols:
        s = df[[date_col] + numeric_cols[:1]].dropna()
        s[date_col] = pd.to_datetime(s[date_col], errors="coerce")
        s = s.dropna().sort_values(date_col).head(100)
        line_labels = [str(x) for x in s[date_col].tolist()]
        line_values = [float(x) for x in s[numeric_cols[0]].tolist()]
    if not line_labels and numeric_cols:
        line_values = df[numeric_cols[0]].dropna().astype(float).head(100).tolist()
        line_labels = [str(i) for i in range(len(line_values))]

    # Categorical value counts
    cat_charts = []
    for col in cat_cols[:5]:
        vc = df[col].dropna().value_counts().head(15)
        cat_charts.append({
            "column": col,
            "labels": [_safe_serialize(k) for k in vc.index.tolist()],
            "values": [int(x) for x in vc.values.tolist()],
        })

    # Histogram data (first numeric column)
    hist_labels, hist_values = [], []
    if numeric_cols:
        ser = df[numeric_cols[0]].dropna().astype(float)
        if len(ser) > 0:
            counts, edges = np.histogram(ser, bins=min(20, max(5, len(ser) // 10)))
            hist_labels = [round(float(e), 2) for e in edges[:-1]]
            hist_values = [int(c) for c in counts]

    # Scatter: first two numeric columns
    scatter_x, scatter_y = [], []
    if len(numeric_cols) >= 2:
        sub = df[numeric_cols[:2]].dropna().head(200)
        scatter_x = [float(x) for x in sub[numeric_cols[0]]]
        scatter_y = [float(y) for y in sub[numeric_cols[1]]]

    # Geo
    lat_col, lon_col, country_col = _detect_geo_columns(df)
    geo_points = []
    geo_countries = []
    if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
        pts = df[[lat_col, lon_col]].dropna().astype(float)
        geo_points = [[float(row[lat_col]), float(row[lon_col])] for _, row in pts.head(200).iterrows()]
    if country_col:
        geo_countries = df[country_col].dropna().astype(str).unique().tolist()[:50]

    return {
        "filename": path.name,
        "sheet": name,
        "rows": len(df),
        "columns": list(df.columns),
        "numeric": numeric_cols,
        "categorical": cat_cols,
        "missing_pct": missing_pct,
        "missing_by_col": missing_by_col,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": duplicate_pct,
        "correlations": correlations,
        "outliers": outliers,
        "anomaly": anomaly,
        "preview": preview,
        "chart_data": {
            "line": {"labels": line_labels, "values": line_values, "label": numeric_cols[0] if numeric_cols else "Value"},
            "categorical": cat_charts,
            "histogram": {"labels": hist_labels, "values": hist_values, "column": numeric_cols[0] if numeric_cols else None},
            "scatter": {"x": scatter_x, "y": scatter_y, "x_label": numeric_cols[0] if len(numeric_cols) > 0 else "", "y_label": numeric_cols[1] if len(numeric_cols) > 1 else ""},
            "geo_points": geo_points,
            "geo_countries": geo_countries,
        },
    }


def get_analysis_results():
    """Analyze all uploaded CSV/Excel files and return results with chart data and KPIs."""
    results = []
    if not UPLOAD_DIR.exists():
        return results
    for path in UPLOAD_DIR.iterdir():
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in CSV_EXT:
            try:
                results.append(analyze_dataset(path))
            except Exception as e:
                print(f"Error analyzing {path.name}: {e}")
        elif suffix in EXCEL_EXT:
            try:
                sheets = _read_file(path)
                for sheet_name, _ in sheets:
                    results.append(analyze_dataset(path, sheet_name=sheet_name))
            except Exception as e:
                print(f"Error analyzing {path.name}: {e}")
    return [r for r in results if r is not None]


def get_dashboard_summary(analysis_results: list) -> dict:
    """Aggregate KPIs for dashboard header cards. Color coding: green / yellow / red."""
    if not analysis_results:
        return {
            "total_datasets": 0,
            "total_rows": 0,
            "total_columns": 0,
            "total_numeric": 0,
            "total_categorical": 0,
            "overall_missing_pct": 0.0,
            "total_duplicates": 0,
            "anomaly_count": 0,
            "status_missing": "green",
            "status_duplicates": "green",
            "status_anomaly": "green",
        }
    total_rows = sum(r["rows"] for r in analysis_results)
    total_columns = sum(len(r["columns"]) for r in analysis_results)
    total_numeric = sum(len(r["numeric"]) for r in analysis_results)
    total_categorical = sum(len(r["categorical"]) for r in analysis_results)
    total_cells = sum(r["rows"] * len(r["columns"]) for r in analysis_results)
    missing_cells = sum(r["rows"] * len(r["columns"]) * (r["missing_pct"] / 100.0) for r in analysis_results)
    overall_missing_pct = round(100.0 * missing_cells / total_cells, 1) if total_cells else 0
    total_duplicates = sum(r["duplicate_rows"] for r in analysis_results)
    anomaly_count = sum(1 for r in analysis_results if r.get("anomaly"))

    def status(pct, low=5, high=15):
        if pct <= low:
            return "green"
        if pct <= high:
            return "yellow"
        return "red"

    return {
        "total_datasets": len(analysis_results),
        "total_rows": total_rows,
        "total_columns": total_columns,
        "total_numeric": total_numeric,
        "total_categorical": total_categorical,
        "overall_missing_pct": overall_missing_pct,
        "total_duplicates": total_duplicates,
        "anomaly_count": anomaly_count,
        "status_missing": status(overall_missing_pct),
        "status_duplicates": status(100.0 * total_duplicates / total_rows if total_rows else 0),
        "status_anomaly": "red" if anomaly_count > 0 else "green",
    }
