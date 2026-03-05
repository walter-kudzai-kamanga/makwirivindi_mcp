from fastapi import APIRouter
router = APIRouter()

@router.get("/question")
def ask_ai():
    return {"answer": "AI Data Question placeholder"}