from fastapi import FastAPI
from routers import upload_router, dashboard_router, settings_router, ai_router, analyze_router, dashboard_api_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(upload_router.router, prefix="/upload")
app.include_router(settings_router.router, prefix="/settings")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(dashboard_router.router, prefix="/dashboard")
app.include_router(dashboard_api_router.router, prefix="/api")
app.include_router(ai_router.router, prefix="/ai")
app.include_router(analyze_router.router)
@app.get("/")
def home():
    return {"message": "Welcome to AI Data Analytics MCP"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)