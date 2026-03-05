from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List
from pathlib import Path
import shutil
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# GET: show upload form
@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# POST: save uploaded files and redirect to processing page
@router.post("/", response_class=HTMLResponse)
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    saved_files = []

    for f in files:
        if not f.filename:
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