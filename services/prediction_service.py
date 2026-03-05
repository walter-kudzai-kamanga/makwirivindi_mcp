"""Simple predictive / trend summaries from analysis results."""


def predict_trends(analysis_results: list) -> dict:
    """
    Return trend prediction and confidence-style summary.
    Example: "Sales predicted to increase 15% next month based on dataset X."
    """
    if not analysis_results:
        return {
            "prediction": "No data available for predictions. Upload and analyze datasets first.",
            "confidence": "low",
            "trend": "neutral",
        }

    total_rows = sum(r["rows"] for r in analysis_results)
    has_numeric = any(r.get("numeric") for r in analysis_results)
    has_time = any(
        (r.get("chart_data") or {}).get("line", {}).get("values")
        for r in analysis_results
    )

    if has_time and has_numeric:
        first = analysis_results[0]
        name = first["filename"] + (" (" + first.get("sheet", "") + ")" if first.get("sheet") and first.get("sheet") != "data" else "")
        return {
            "prediction": f"Trend analysis is available for '{name}'. Use the line chart and filters to explore time-based trends. With more historical data, we can add formal forecasts.",
            "confidence": "medium",
            "trend": "explore",
        }

    if has_numeric:
        return {
            "prediction": f"You have {total_rows} rows across {len(analysis_results)} dataset(s). Numeric columns are available for correlation and scatter analysis. Add a date column for time-series forecasts.",
            "confidence": "medium",
            "trend": "neutral",
        }

    return {
        "prediction": "Categorical and count data detected. Upload datasets with numeric or date columns for trend predictions and forecasts.",
        "confidence": "low",
        "trend": "neutral",
    }
