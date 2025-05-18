import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

BOT_TOKEN = os.getenv("7647337975:AAGUtM4h0B3sW2VyLsLZBxr6XKXmbK_hCG8")
CHANNEL_ID = os.getenv("-1002523004984")  # e.g. "-1001234567890"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

@app.post("/")
async def webhook(request: Request):
    update = await request.json()
    message = update.get("message")
    if not message:
        return JSONResponse({"ok": True})

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    async with httpx.AsyncClient() as client:
        # Forward message to channel
        await client.post(f"{API_URL}forwardMessage", json={
            "chat_id": CHANNEL_ID,
            "from_chat_id": chat_id,
            "message_id": message_id
        })

    return JSONResponse({"ok": True})
