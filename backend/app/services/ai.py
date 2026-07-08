import os
import json
import httpx

from app.services.mcp import (
    get_mcp_tools,
    execute_mcp_tool
)


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4.1-mini"
)


print(
    "OPENROUTER_API_KEY EXISTS:",
    bool(OPENROUTER_API_KEY)
)

print(
    "OPENROUTER_MODEL:",
    MODEL
)


SYSTEM_PROMPT = """
Ты AI ассистент управления диаграммой Ганта.

Главное правило:
Работай ТОЛЬКО с задачами из context.tasks.

Перед любым действием:

1. Найди задачу в context.tasks.
2. Сравни название задачи с text.
3. Используй существующий id этой задачи.
4. Никогда не придумывай id.
5. Если задача не найдена — НЕ вызывай инструменты.

Удаление задачи:

Пользователь:
удали задачу лосось

Если есть:

{
"id":"temp://1783455853275",
"text":"лосось"
}

Вызови:

delete_task(
 task_id="temp://1783455853275"
)

Создание задачи:

Пользователь:
Добавь задачу маркетинговые исследования

Вызови:

create_task(
 text="Маркетинговые исследования"
)

Обновление задачи:

Пользователь:
Поставь Backend API 100%

Вызови:

update_task(
 task_id=id,
 progress=100
)

После выполнения возвращай только JSON.

Не объясняй действия.
"""


async def ask_ai(
    message: str,
    context: dict
):

    if not OPENROUTER_API_KEY:

        return {
            "action": "error",
            "message": "OPENROUTER_API_KEY is missing"
        }


    mcp_tools = await get_mcp_tools()

    tools = []

    for tool in mcp_tools:

        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
        )


    async with httpx.AsyncClient(
        timeout=120
    ) as client:

        response = await client.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",
            },

            json={

                "model": MODEL,

                "messages": [

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "message": message,
                                "context": context
                            },
                            ensure_ascii=False
                        )
                    }

                ],

                "tools": tools,

                "tool_choice": "auto",

                "temperature": 0
            }
        )


    data = response.json()


    print(
        "OPENROUTER RESPONSE:",
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )
    )


    if "choices" not in data:

        return {
            "action": "error",
            "message": data
        }


    ai_message = data["choices"][0]["message"]


    tool_calls = ai_message.get(
        "tool_calls"
    )


    if tool_calls:

        tool_call = tool_calls[0]

        tool_name = tool_call["function"]["name"]

        arguments = json.loads(
            tool_call["function"]["arguments"]
        )


        print(
            "MCP CALL:",
            tool_name,
            arguments
        )


        result = await execute_mcp_tool(
            tool_name,
            arguments
        )


        print(
            "MCP RESULT:",
            result
        )


        try:
            result = json.loads(result)

        except:

            pass


        if tool_name == "delete_task":

            return {
                "action": "delete_task",
                "data": {
                    "id": arguments["task_id"]
                }
            }


        if tool_name == "create_task":

            return {
                "action": "create_task",
                "data": {
                    "task": result["task"]
                }
            }


        if tool_name in [
            "update_task",
            "update_task_progress",
            "update_task_assignee"
        ]:

            return {
                "action": "update_task",
                "data": {
                    "id": arguments["task_id"],
                    "changes": arguments
                }
            }


    content = ai_message.get(
        "content",
        ""
    )


    if content:

        try:

            parsed = json.loads(content)

            if parsed.get("action") in [
                "delete_task",
                "create_task",
                "update_task"
            ]:

                return parsed

        except Exception:

            pass


    return {
        "action": "message",
        "message": content or "AI не вернул ответ"
    }