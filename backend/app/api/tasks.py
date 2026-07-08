from fastapi import APIRouter
from app.state import gantt_state

router = APIRouter()

@router.get("/tasks")
def get_tasks():
    return gantt_state.tasks