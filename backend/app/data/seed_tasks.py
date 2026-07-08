from datetime import datetime
from fastapi import FastAPI

app = FastAPI()


def to_iso(dt):
    return dt.isoformat() if isinstance(dt, datetime) else None


tasks = [
    {
        "id": 1,
        "text": "Разработка продукта",
        "type": "summary",
        "open": True,
        "assignee": "Команда",
        "start": None,
        "duration": 0,
        "progress": 0,
        "parent": None,
    },
    {
        "id": 2,
        "text": "Сбор требований и архитектура",
        "type": "task",
        "start": datetime(2026, 7, 1),
        "duration": 2,
        "progress": 100,
        "parent": 1,
        "assignee": "Алексей",
    },
    {
        "id": 3,
        "text": "Backend API (FastAPI)",
        "type": "task",
        "start": datetime(2026, 7, 3),
        "duration": 4,
        "progress": 60,
        "parent": 1,
        "assignee": "Иван",
    },
    {
        "id": 4,
        "text": "Frontend (React + UI)",
        "type": "task",
        "start": datetime(2026, 7, 5),
        "duration": 5,
        "progress": 50,
        "parent": 1,
        "assignee": "Мария",
    },
    {
        "id": 5,
        "text": "Интеграция frontend + backend",
        "type": "task",
        "start": datetime(2026, 7, 9),
        "duration": 2,
        "progress": 30,
        "parent": 1,
        "assignee": "Ольга",
    },
    {
        "id": 6,
        "text": "Тестирование и багфикс",
        "type": "task",
        "start": datetime(2026, 7, 11),
        "duration": 3,
        "progress": 10,
        "parent": 1,
        "assignee": "Алексей",
    },
]


@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "id": t["id"],
                "text": t.get("text", ""),
                "type": t.get("type", "task"),

                "start": to_iso(t.get("start")) or "2026-07-01T00:00:00",

                "duration": 0 if t.get("type") == "summary" else (t.get("duration") or 1),

                "progress": t.get("progress") or 0,
                "open": t.get("open", True),
                "parent": t.get("parent"),

                "assignee": t.get("assignee", ""),
            }
            for t in tasks
        ]
    }