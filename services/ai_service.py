"""Generate natural-language and structured insights from analysis results."""


def generate_insights(analysis_results: list) -> list:
    """
    Build insights from analysis_results: top correlations, missing data, outliers,
    and distribution hints for categorical variables.
    """
    insights = []
    if not analysis_results:
        insights.append("No datasets analyzed yet. Upload CSV or Excel files to get insights.")
        return insights

    for result in analysis_results:
        label = result["filename"] + (" (" + result.get("sheet", "") + ")" if result.get("sheet") and result.get("sheet") != "data" else "")

        # Correlations
        corrs = result.get("correlations") or []
        if corrs:
            top = corrs[0]
            insights.append(
                f"[{label}] Strongest correlation: {top['col1']} vs {top['col2']} (r = {top['value']})."
            )
            for c in corrs[1:4]:
                insights.append(
                    f"[{label}] Correlation: {c['col1']} ↔ {c['col2']} = {c['value']}."
                )

        # Missing data
        missing_pct = result.get("missing_pct", 0)
        missing_by_col = result.get("missing_by_col") or {}
        high_missing = [col for col, pct in missing_by_col.items() if pct > 5]
        if missing_pct > 0:
            insights.append(
                f"[{label}] Missing data: {missing_pct}% overall."
                + (f" Columns with >5% missing: {', '.join(high_missing[:5])}." if high_missing else "")
            )

        # Outliers
        outliers = result.get("outliers") or []
        if outliers:
            parts = [f"{o['column']} ({o['outlier_count']} outliers)" for o in outliers[:5]]
            insights.append(f"[{label}] Potential outliers (IQR): " + "; ".join(parts) + ".")

        # Categorical distribution
        cat_charts = (result.get("chart_data") or {}).get("categorical") or []
        for cat in cat_charts[:2]:
            if cat.get("labels") and cat.get("values"):
                n_cats = len(cat["labels"])
                insights.append(
                    f"[{label}] Categorical column '{cat['column']}' has {n_cats} distinct values; "
                    "check bar chart for distribution."
                )

    if not insights:
        insights.append("No specific insights generated. Add more data or numeric columns for correlations and outlier detection.")
    return insights[:25]  # Cap for UI
