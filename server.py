from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv
from llm import generate_reply
from memory import reset_memory

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = FastAPI()


def send_typing(chat_id):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",
        params={"chat_id": chat_id, "action": "typing"}
    )


@app.get("/webhook")
async def ignore_get():
    return {"ok": True}


@app.get("/favicon.ico")
async def ignore_favicon():
    return {"ok": True}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # /reset
        if text.strip().lower() == "/reset":
            reset_memory(chat_id)
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "🧹 Memory cleared.",
                    "parse_mode": "HTML"
                }
            )
            return {"ok": True}

        send_typing(chat_id)

        reply = generate_reply(chat_id, text)

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": reply,
                "parse_mode": "HTML"
            }
        )

    return {"ok": True}
