"""Company settings: logo upload. Protected by access key when UPLOAD_ACCESS_KEY is set."""
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config import require_access_key, UPLOAD_ACCESS_KEY

router = APIRouter()
templates = Jinja2Templates(directory="templates")

STATIC_DIR = Path("static")
LOGO_PATH = STATIC_DIR / "logo.png"
ALLOWED_LOGO_EXT = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


def _check_access(access_key: str | None) -> bool:
    if not require_access_key():
        return True
    return access_key == UPLOAD_ACCESS_KEY


@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    logo_mtime = int(LOGO_PATH.stat().st_mtime) if LOGO_PATH.exists() else 0
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "require_access_key": require_access_key(),
        "logo_exists": LOGO_PATH.exists(),
        "logo_mtime": logo_mtime,
    })


@router.post("/logo")
async def upload_logo(
    request: Request,
    logo: UploadFile = File(None),
    access_key: str = Form(None),
):
    if not _check_access(access_key):
        return JSONResponse({"detail": "Access denied. Invalid access key."}, status_code=403)

    if not logo or not logo.filename:
        return RedirectResponse(url="/settings/", status_code=303)

    ext = Path(logo.filename).suffix.lower()
    if ext not in ALLOWED_LOGO_EXT:
        return JSONResponse(
            {"detail": f"Invalid format. Allowed: {', '.join(ALLOWED_LOGO_EXT)}"},
            status_code=400,
        )

    STATIC_DIR.mkdir(exist_ok=True)
    content = await logo.read()
    with open(LOGO_PATH, "wb") as f:
        f.write(content)

    return RedirectResponse(url="/settings/", status_code=303)
