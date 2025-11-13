# llm.py
import requests

def generate_reply(prompt: str) -> str:
    body = {
        "model": "local",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    resp = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json=body,
        headers={"Authorization": "Bearer lm-studio"}
    )

    data = resp.json()
    return data["choices"][0]["message"]["content"]
