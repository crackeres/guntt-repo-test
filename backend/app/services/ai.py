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

Работай только с задачами из context.tasks.

Перед действием:
1. Найди задачу в context.tasks.
2. Используй существующий id.
3. Никогда не придумывай id.
4. Если задачи нет — верни message.

Создание:
Используй create_task.

Обновление:
Используй update_task.

Удаление:
Используй delete_task.

После ответа:
Если вызываешь инструмент — используй tool_calls.

Если инструмент не нужен — верни JSON:

{
 "action":"message",
 "message":"текст"
}

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


    payload = {

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


    print(
        "AI REQUEST:",
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False
        )
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
                    "application/json"
            },

            json=payload

        )


    print(
        "OPENROUTER STATUS:",
        response.status_code
    )


    raw = response.text


    print(
        "OPENROUTER RAW:",
        raw
    )


    try:

        data = response.json()

    except Exception:

        return {
            "action": "error",
            "message": raw
        }



    if "choices" not in data:

        return {
            "action": "error",
            "message": data
        }



    ai_message = data["choices"][0]["message"]


    print(
        "AI MESSAGE:",
        json.dumps(
            ai_message,
            indent=2,
            ensure_ascii=False
        )
    )



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
                    "task": result.get("task")
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
                    "id": arguments.get("task_id"),
                    "changes": arguments
                }
            }



    content = ai_message.get(
        "content"
    )


    if content:


        try:

            parsed = json.loads(content)

            return parsed


        except Exception:

            return {
                "action": "message",
                "message": content
            }



    return {
        "action": "message",
        "message": "AI returned empty response"
    }