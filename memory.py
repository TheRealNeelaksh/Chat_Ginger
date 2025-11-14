import os
import json
import time

MEMORY_DIR = "memory"
MAX_MESSAGES = 20                      # rolling window
EXPIRY_SECONDS = 2 * 24 * 3600         # 2 days

os.makedirs(MEMORY_DIR, exist_ok=True)


def get_memory_path(chat_id):
    return os.path.join(MEMORY_DIR, f"{chat_id}.json")


def load_memory(chat_id):
    path = get_memory_path(chat_id)

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return []

    now = time.time()

    # Filter expired messages
    data = [m for m in data if now - m["timestamp"] <= EXPIRY_SECONDS]

    return data


def save_memory(chat_id, messages):
    path = get_memory_path(chat_id)
    messages = messages[-MAX_MESSAGES:]  # rolling window

    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)


def append_memory(chat_id, role, content):
    msgs = load_memory(chat_id)
    msgs.append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })
    save_memory(chat_id, msgs)


def reset_memory(chat_id):
    path = get_memory_path(chat_id)
    if os.path.exists(path):
        os.remove(path)
