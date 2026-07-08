from fastapi import APIRouter, UploadFile, File
import pandas as pd

from app.state import gantt_state

router = APIRouter()


@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):

    print("UPLOAD START:", file.filename)


    try:

        df = pd.read_excel(
            file.file,
            engine="openpyxl"
        )


        print(
            "EXCEL LOADED:",
            df.head()
        )


        tasks = []


        for i, row in df.iterrows():

            task = {
                "id": i + 1,
                "text": str(
                    row.get(
                        "Задача",
                        "Без названия"
                    )
                ),

                "description": str(
                    row.get(
                        "Описание",
                        ""
                    )
                ),

                "assignee": str(
                    row.get(
                        "Исполнитель",
                        ""
                    )
                ),

                "duration": int(
                    row.get(
                        "Длительность",
                        1
                    )
                ),

                "dependencies": []
            }


            tasks.append(task)



        gantt_state.tasks = tasks


        print(
            "TASKS SAVED:",
            len(tasks)
        )


        return {
            "tasks": tasks
        }


    except Exception as e:

        print(
            "UPLOAD ERROR:",
            repr(e)
        )


        return {
            "error": str(e)
        }