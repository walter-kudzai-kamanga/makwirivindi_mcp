"""API endpoints for dashboard: delete dataset, export dataset/report."""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import pandas as pd
import io

from services.analysis_service import UPLOAD_DIR, get_analysis_results, analyze_dataset, CSV_EXT, EXCEL_EXT

router = APIRouter()


@router.delete("/datasets/{filename:path}")
async def delete_dataset(filename: str):
    """Delete an uploaded file by name. Only allows files in uploads dir."""
    base = UPLOAD_DIR.resolve()
    path = (UPLOAD_DIR / filename).resolve()
    if not path.is_file() or not str(path).startswith(str(base)):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        path.unlink()
        return JSONResponse({"status": "success", "message": f"Deleted {filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/dataset")
async def export_dataset(filename: str, sheet: str | None = None):
    """
    Export a dataset as CSV. For Excel files, specify sheet to export that sheet as CSV.
    Without sheet, returns the original file (Excel or CSV).
    """
    path = UPLOAD_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    suffix = path.suffix.lower()
    if suffix not in CSV_EXT and suffix not in EXCEL_EXT:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if sheet and suffix in EXCEL_EXT:
        try:
            df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl" if suffix == ".xlsx" else None)
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            buf.seek(0)
            return StreamingResponse(
                iter([buf.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{path.stem}_{sheet}.csv"'},
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(path, filename=path.name, media_type="application/octet-stream")


@router.get("/export/report")
async def export_report():
    """Export a simple text report of current analysis (summary + file list)."""
    results = get_analysis_results()
    lines = ["Makwirivindi Analytics – Report", "=" * 40, ""]
    for r in results:
        lines.append(f"Dataset: {r['filename']}" + (f" (sheet: {r.get('sheet')})" if r.get("sheet") and r.get("sheet") != "data" else ""))
        lines.append(f"  Rows: {r['rows']}, Columns: {len(r['columns'])}")
        lines.append(f"  Missing: {r.get('missing_pct', 0)}%, Duplicates: {r.get('duplicate_rows', 0)}")
        lines.append("")
    buf = io.BytesIO("\n".join(lines).encode("utf-8"))
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/plain",
        headers={"Content-Disposition": 'attachment; filename="makwirivindi_report.txt"'},
    )
