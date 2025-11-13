# llm.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("LMSTUDIO_API_URL")   # ex: http://172.16.0.2:7007/v1
MODEL = os.getenv("LMSTUDIO_MODEL")        # ex: meta-llama-3-8b-instruct
API_KEY = os.getenv("LMSTUDIO_KEY", "lm-studio")


def generate_reply(user_text: str) -> str:
    url = f"{BASE_URL}/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "stream": False
    }

    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )

        print("LMStudio status:", resp.status_code)
        print("LMStudio response:", resp.text)

        resp.raise_for_status()
        data = resp.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("LM Studio ERROR:", e)
        return "⚠️ Model offline or failed to respond."
