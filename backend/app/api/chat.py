from fastapi import APIRouter, Request
from app.services.ai import ask_ai
import traceback


router = APIRouter()


@router.post("/chat")
async def chat(request: Request):

    try:

        body = await request.json()

        print(
            "📥 CHAT REQUEST:",
            body
        )


        result = await ask_ai(
            body["message"],
            body["context"]
        )


        print(
            "📤 RESULT:",
            result
        )


        return result


    except Exception as e:

        traceback.print_exc()

        return {
            "error": str(e)
        }