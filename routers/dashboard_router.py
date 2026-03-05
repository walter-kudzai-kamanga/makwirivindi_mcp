from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.ai_service import generate_insights
from services.analysis_service import analyze_dataset, get_analysis_results
from pathlib import Path

from services.prediction_service import predict_trends

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = Path("uploads")


@router.get("/", response_class=None)
def dashboard(request: Request):
    analysis_results = get_analysis_results()               # Get real analysis
    insights = generate_insights(analysis_results)          # AI insights
    predictions = predict_trends(analysis_results)          # Predictions
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "analysis_results": analysis_results,
        "insights": insights,
        "predictions": predictions
    })