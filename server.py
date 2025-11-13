# server.py
from fastapi import FastAPI, Request
import requests
import os
from llm import generate_reply

TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = generate_reply(text)

        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={"chat_id": chat_id, "text": reply}
        )

    return {"ok": True}
