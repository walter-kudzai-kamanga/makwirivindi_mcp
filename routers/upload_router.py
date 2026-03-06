from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List
import shutil
import os

from config import require_access_key, UPLOAD_ACCESS_KEY

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def _check_access(access_key: str | None) -> bool:
    if not require_access_key():
        return True
    return access_key == UPLOAD_ACCESS_KEY


# GET: show upload form
@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "require_access_key": require_access_key(),
    })


# POST: save uploaded files and redirect to processing page
@router.post("/", response_class=HTMLResponse)
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...),
    access_key: str = Form(None),
):
    if not _check_access(access_key):
        return JSONResponse({"detail": "Access denied. Invalid or missing access key."}, status_code=403)
    saved_files = []

    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        safe_filename = os.path.basename(f.filename)
        file_path = UPLOAD_DIR / safe_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_files.append(safe_filename)

    if not saved_files:
        return {"message": "No valid files uploaded."}

    # Pass saved filenames to processing page
    return templates.TemplateResponse(
        "processing.html",
        {"request": request, "files": saved_files}
    )