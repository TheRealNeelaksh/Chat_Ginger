# bot.py
import os
import requests
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
NGROK_URL = os.getenv("STATIC_NGROK_DOMAIN")

resp = requests.get(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    params={"url": NGROK_URL + "/webhook"}
)

print(resp.json())
