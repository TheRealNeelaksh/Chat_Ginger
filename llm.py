import os
import requests
from dotenv import load_dotenv
from memory import load_memory, append_memory

load_dotenv()

BASE_URL = os.getenv("LMSTUDIO_API_URL")
MODEL = os.getenv("LMSTUDIO_MODEL")
API_KEY = os.getenv("LMSTUDIO_KEY", "lm-studio")


def escape_html(text: str) -> str:
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_reply(chat_id, user_text: str) -> str:

    # Load per-user chat history
    history = load_memory(chat_id)

    # Append user message
    append_memory(chat_id, "user", user_text)

    # Convert memory to LM format
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300,
        "stream": False
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )

        print("LMStudio status:", resp.status_code)
        print("LMStudio response:", resp.text)

        resp.raise_for_status()

        reply = resp.json()["choices"][0]["message"]["content"]

        append_memory(chat_id, "assistant", reply)

        return escape_html(reply)

    except Exception as e:
        print("LM Studio ERROR:", e)
        return "⚠️ Model offline or failed to respond."
