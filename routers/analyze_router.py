from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.analysis_service import analyze_dataset
import os

router = APIRouter()

@router.post("/analyze/")
async def analyze():
    upload_dir = "uploads"
    results = []
    for filename in os.listdir(upload_dir):
        path = os.path.join(upload_dir, filename)
        if os.path.isfile(path) and filename.endswith(".csv"):
            analysis = analyze_dataset(path)
            results.append({
                "filename": filename,
                "rows": analysis["rows"],
                "columns": analysis["columns"],
                "numeric": analysis["numeric"],
                "categorical": analysis["categorical"]
            })
    return JSONResponse({"status":"success", "results": results})