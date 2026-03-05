from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.analysis_service import get_analysis_results

router = APIRouter()


@router.post("/analyze/")
async def analyze():
    """Run analysis on all uploaded CSV/Excel files and return results with chart data."""
    results = get_analysis_results()
    return JSONResponse({"status": "success", "results": results})