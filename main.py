import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

BOT_TOKEN = os.getenv("7647337975:AAGUtM4h0B3sW2VyLsLZBxr6XKXmbK_hCG8")
TARGET_USER_ID = 1366000165  # Replace with your actual user ID
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message")

    if message:
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]

        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/forwardMessage", json={
                "chat_id": TARGET_USER_ID,
                "from_chat_id": chat_id,
                "message_id": message_id
            })

    return JSONResponse(content={"ok": True})
