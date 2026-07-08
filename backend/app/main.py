from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.upload_excel import router as upload_router
from app.api.export_excel import router as export_router
from app.api.tasks import router as tasks_router

from app.core.cors import setup_cors


app = FastAPI()

setup_cors(app)


app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(export_router)
app.include_router(tasks_router)