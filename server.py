# server.py
from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv
from llm import generate_reply

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = FastAPI()

LAST_CHAT_ID = None


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
    global LAST_CHAT_ID

    data = await request.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        LAST_CHAT_ID = chat_id

        text = data["message"].get("text", "")

        send_typing(chat_id)

        reply = generate_reply(text)

        if not reply or reply.strip() == "":
            reply = "⚠️ Model offline or failed to respond."

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return {"ok": True}



# -----------------------------
# Safe "bot online" message
# -----------------------------
def send_bot_online_message():
    global LAST_CHAT_ID

    if LAST_CHAT_ID is None:
        print("⚠️ Bot online but no user has messaged yet.")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": LAST_CHAT_ID, "text": "🤖 Bot is online and connected to LM Studio."}
        )
        print("Startup message sent.")

    except Exception as e:
        print("Failed to send startup message:", e)
