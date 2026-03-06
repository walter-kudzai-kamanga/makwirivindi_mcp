from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime

from services.ai_service import generate_insights
from services.analysis_service import get_analysis_results, get_dashboard_summary
from services.prediction_service import predict_trends

router = APIRouter()
LOGO_PATH = Path("static") / "logo.png"
templates = Jinja2Templates(directory="templates")
templates.env.filters["intcomma"] = lambda x: f"{int(x):,}" if x is not None else "0"


def _dataset_display_name(filename: str) -> str:
    """Convert filename to sidebar label, e.g. trade.csv -> Trade, sales_data.xlsx -> Sales Data."""
    stem = Path(filename).stem
    return stem.replace("_", " ").replace("-", " ").title()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    analysis_results = get_analysis_results()
    seen = set()
    unique_datasets = []
    for r in analysis_results:
        if r["filename"] not in seen:
            seen.add(r["filename"])
            unique_datasets.append({
                "filename": r["filename"],
                "display": _dataset_display_name(r["filename"]),
            })
    kpis = get_dashboard_summary(analysis_results)
    insights = generate_insights(analysis_results)
    predictions = predict_trends(analysis_results)
    logo_mtime = int(LOGO_PATH.stat().st_mtime) if LOGO_PATH.exists() else 0
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "analysis_results": analysis_results,
        "unique_datasets": unique_datasets,
        "kpis": kpis,
        "insights": insights,
        "predictions": predictions,
        "now": datetime.utcnow(),
        "logo_mtime": logo_mtime,
    })