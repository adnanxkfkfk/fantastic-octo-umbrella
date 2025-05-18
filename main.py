from fastapi import FastAPI, Request
import os
import httpx
import random

app = FastAPI()

# Bot and Firebase settings
BOT_TOKEN = os.getenv("7647337975:AAGUtM4h0B3sW2VyLsLZBxr6XKXmbK_hCG8")
LOG_CHANNEL = "-1002523004984"
BOT_USERNAME = "File_To_Link_2Bot"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FIREBASE_URL = "https://fran-eb915-default-rtdb.firebaseio.com/files"

def generate_key():
    return ''.join(random.choices('abcdef0123456789', k=16))

async def save_to_firebase(key, file_id):
    async with httpx.AsyncClient() as client:
        await client.put(f"{FIREBASE_URL}/{key}.json", json={"file_id": file_id})

async def get_from_firebase(key):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{FIREBASE_URL}/{key}.json")
        if res.status_code == 200:
            data = res.json()
            return data.get("file_id")
        return None

@app.post("/")
async def webhook(req: Request):
    data = await req.json()

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        msg_id = msg["message_id"]

        # Save file
        for kind in ["document", "video", "audio", "photo"]:
            if kind in msg:
                file_id = msg[kind][-1]["file_id"] if kind == "photo" else msg[kind]["file_id"]
                key = generate_key()
                await save_to_firebase(key, file_id)

                async with httpx.AsyncClient() as client:
                    # Forward to log channel
                    await client.post(f"{API_URL}/copyMessage", json={
                        "chat_id": LOG_CHANNEL,
                        "from_chat_id": chat_id,
                        "message_id": msg_id
                    })
                    # Reply with download link
                    await client.post(f"{API_URL}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": f"✅ File saved!\n\nGet it anytime from:\nhttps://t.me/{BOT_USERNAME}?start=file_{key}"
                    })
                break

        # Handle download link
        if "text" in msg and msg["text"].startswith("/start file_"):
            key = msg["text"].split("_")[1]
            file_id = await get_from_firebase(key)
            async with httpx.AsyncClient() as client:
                if file_id:
                    await client.post(f"{API_URL}/sendDocument", json={
                        "chat_id": chat_id,
                        "document": file_id
                    })
                else:
                    await client.post(f"{API_URL}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": "⚠️ File not found or expired."
                    })

    return {"ok": True}
