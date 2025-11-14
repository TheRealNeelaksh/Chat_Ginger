import os
import subprocess
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")


def send_startup_message():
    if not OWNER_CHAT_ID:
        print("⚠️ OWNER_CHAT_ID missing, cannot send startup message.")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": OWNER_CHAT_ID,
                "text": "🤖 Ginger is online.\nLM Studio connected.\nngrok tunnel active.\nReady.",
                "parse_mode": "HTML"
            }
        )
        print("Startup message sent.")
    except Exception as e:
        print("Failed to send startup message:", e)


def start_ngrok():
    print("Starting ngrok tunnel...")

    # Ensure ngrok authtoken is registered
    subprocess.run(["ngrok", "config", "add-authtoken", NGROK_AUTHTOKEN])

    ngrok = subprocess.Popen(
        ["ngrok", "http", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(3)

    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        public_url = tunnels["tunnels"][0]["public_url"]
        print("ngrok URL:", public_url)
        return public_url, ngrok
    except:
        print("❌ Failed to get ngrok URL")
        return None, ngrok


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

    public_url, ngrok_proc = start_ngrok()
    if not public_url:
        exit()

    api_proc = start_server()

    time.sleep(3)
    set_webhook(public_url)

    send_startup_message()

    print("Bot is LIVE.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        ngrok_proc.terminate()
        api_proc.terminate()
        print("Stopped.")
