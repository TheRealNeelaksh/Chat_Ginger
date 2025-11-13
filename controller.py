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

import subprocess
import time
import requests
import psutil

def start_ngrok():
    print("Checking for existing ngrok tunnel...")

    # First: try reading existing tunnel (4040 API)
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2).json()
        if "tunnels" in tunnels and len(tunnels["tunnels"]) > 0:
            url = tunnels["tunnels"][0]["public_url"]
            print("Reusing existing ngrok URL:", url)
            return url, None
    except:
        pass  # panel wasn't running, so ngrok not active

    # If ngrok was partially running but broken, kill all processes
    print("No active tunnel. Killing zombie ngrok processes...")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "ngrok" in proc.info['name'].lower():
            try:
                proc.kill()
                print("Killed:", proc.pid)
            except:
                pass

    time.sleep(1)

    print("Starting fresh ngrok...")
    ngrok = subprocess.Popen(
        ["ngrok", "http", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Retry until tunnel appears
    for _ in range(10):
        try:
            time.sleep(1)
            tunnels = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2).json()
            if "tunnels" in tunnels and len(tunnels["tunnels"]) > 0:
                url = tunnels["tunnels"][0]["public_url"]
                print("ngrok started:", url)
                return url, ngrok
        except:
            pass

    print("❌ Failed to start ngrok tunnel after retries.")
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
