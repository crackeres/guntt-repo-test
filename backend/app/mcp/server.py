from mcp.server.fastmcp import FastMCP
from typing import Optional
import json
import os


mcp = FastMCP("gantt-ai")


TASKS_FILE = "app/mcp/tasks.json"


def load_tasks():

    if not os.path.exists(TASKS_FILE):

        return [
            {
                "id": 1,
                "text": "Сбор требований",
                "progress": 50,
                "duration": 5,
                "assignee": "Алексей",
                "parent": None,
            }
        ]


    with open(
        TASKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def save_tasks(tasks):

    with open(
        TASKS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            tasks,
            file,
            ensure_ascii=False,
            indent=2
        )



tasks = load_tasks()



@mcp.tool()
def get_tasks():
    """
    Получить список всех задач.
    """

    return tasks



@mcp.tool()
def get_task(task_id: int):
    """
    Получить задачу по ID.
    """

    for task in tasks:

        if task["id"] == task_id:

            return task


    return {
        "error": "Task not found"
    }



@mcp.tool()
def create_task(
    text: str,
    duration: int = 1,
    assignee: Optional[str] = "",
    parent: Optional[int] = None
):
    """
    Создать новую задачу.
    """

    new_id = max(
        [
            task["id"]
            for task in tasks
        ],
        default=0
    ) + 1


    new_task = {

        "id": new_id,

        "text": text,

        "progress": 0,

        "duration": duration,

        "assignee": assignee,

        "parent": parent

    }


    tasks.append(new_task)

    save_tasks(tasks)


    return {

        "success": True,

        "action": "create_task",

        "task": new_task

    }



@mcp.tool()
def update_task(
    task_id: int,
    text: Optional[str] = None,
    progress: Optional[int] = None,
    duration: Optional[int] = None,
    assignee: Optional[str] = None,
    parent: Optional[int] = None
):
    """
    Обновить параметры задачи.
    """

    for task in tasks:

        if task["id"] == task_id:


            if text is not None:
                task["text"] = text


            if progress is not None:
                task["progress"] = progress


            if duration is not None:
                task["duration"] = duration


            if assignee is not None:
                task["assignee"] = assignee


            if parent is not None:
                task["parent"] = parent


            save_tasks(tasks)


            return {

                "success": True,

                "action": "update_task",

                "task": task

            }


    return {

        "error": "Task not found"

    }



@mcp.tool()
def delete_task(task_id: int):
    """
    Удалить задачу.
    """

    global tasks


    exists = any(
        task["id"] == task_id
        for task in tasks
    )


    if not exists:

        return {

            "error": "Task not found"

        }


    tasks = [

        task

        for task in tasks

        if task["id"] != task_id

    ]


    save_tasks(tasks)


    return {

        "success": True,

        "action": "delete_task",

        "id": task_id

    }



@mcp.tool()
def update_task_progress(
    task_id: int,
    progress: int
):
    """
    Изменить только прогресс задачи.
    """

    return update_task(
        task_id=task_id,
        progress=progress
    )



@mcp.tool()
def update_task_assignee(
    task_id: int,
    assignee: str
):
    """
    Изменить исполнителя задачи.
    """

    return update_task(
        task_id=task_id,
        assignee=assignee
    )



@mcp.tool()
def move_task(
    task_id: int,
    parent: Optional[int] = None
):
    """
    Переместить задачу к другому родителю.
    """

    return update_task(
        task_id=task_id,
        parent=parent
    )



if __name__ == "__main__":

    mcp.run()