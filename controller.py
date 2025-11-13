# controller.py
import os
import subprocess
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")

from server import send_bot_online_message

def start_ngrok():
    print("Starting ngrok tunnel...")
    ngrok = subprocess.Popen(
        ["ngrok", "http", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(3)  # give ngrok time to boot

    # Fetch public URL
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        public_url = tunnels["tunnels"][0]["public_url"]
    except:
        print("❌ Failed to get ngrok URL")
        return None, ngrok

    print("ngrok URL:", public_url)
    return public_url, ngrok


def start_server():
    print("Starting FastAPI server...")
    return subprocess.Popen(["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"])


def set_webhook(public_url):
    webhook_url = f"{public_url}/webhook"
    print("Setting webhook:", webhook_url)

    r = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        params={"url": webhook_url}
    )
    print(r.json())


if __name__ == "__main__":
    print("=== LM Studio Telegram Bot Launcher ===")

    # Start ngrok
    public_url, ngrok_proc = start_ngrok()
    if not public_url:
        exit()

    # Start FastAPI
    api_proc = start_server()

    # Register webhook
    time.sleep(3)
    set_webhook(public_url)

    # Notify user if possible
    send_bot_online_message()

    print("Bot is LIVE. Send messages in Telegram.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        ngrok_proc.terminate()
        api_proc.terminate()
        print("Stopped.")
