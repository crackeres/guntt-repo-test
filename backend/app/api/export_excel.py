from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from app.state import gantt_state

router = APIRouter()

@router.get("/export-excel")
def export_excel():

    print(gantt_state.tasks)

    data = gantt_state.tasks

    df = pd.DataFrame(data)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Gantt")

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=gantt.xlsx"
        }
    )