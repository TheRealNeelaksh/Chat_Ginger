# controller.py
import os
import subprocess
import time
import json
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()

NGROK_DOMAIN = os.getenv("STATIC_NGROK_DOMAIN")     # e.g. https://yourbot.ngrok-free.app
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")

LMSTUDIO_MODELS_DIR = os.path.expanduser("~/Library/Application Support/LM Studio/models") \
    if os.name == "posix" else os.path.expanduser("~/AppData/Roaming/LM Studio/models")


def list_models():
    models = []
    if os.path.exists(LMSTUDIO_MODELS_DIR):
        for folder in os.listdir(LMSTUDIO_MODELS_DIR):
            models.append(folder)
    return models


def choose_model(models):
    table = Table(title="Installed LM Studio Models")
    table.add_column("Index")
    table.add_column("Model Name")

    for i, m in enumerate(models):
        table.add_row(str(i), m)

    console.print(table)
    idx = int(console.input("\nChoose a model index: "))
    return models[idx]


def choose_gpu():
    console.print("\n[bold]Available GPUs:[/bold]")

    try:
        result = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True)
        gpus = result.decode().strip().split("\n")
    except:
        gpus = ["CPU only"]

    for i, g in enumerate(gpus):
        console.print(f"[cyan]{i}[/cyan] → {g}")

    idx = int(console.input("\nChoose GPU index: "))
    return idx, gpus[idx]


def launch_lmstudio(model, gpu_index):
    console.print(f"\n[green]Launching LM Studio server with model: {model}[/green]")

    cmd = f"""
    lmstudio server start \
        --model "{model}" \
        --port 1234 \
        --gpu {gpu_index}
    """

    return subprocess.Popen(cmd, shell=True)


def launch_ngrok():
    console.print("\n[yellow]Starting ngrok static tunnel...[/yellow]")

    subprocess.run(f"ngrok config add-authtoken {NGROK_AUTHTOKEN}", shell=True)
    subprocess.Popen(f"ngrok http --domain={NGROK_DOMAIN} 8000", shell=True)

    time.sleep(2)
    return NGROK_DOMAIN


def set_webhook(url):
    import requests
    webhook = url + "/webhook"
    console.print(f"\nSetting Telegram webhook to: {webhook}")

    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={"url": webhook})
    console.print(resp.json())


def launch_fastapi():
    console.print("\n[green]Starting FastAPI server...[/green]")
    return subprocess.Popen("uvicorn server:app --host 0.0.0.0 --port 8000", shell=True)


if __name__ == "__main__":
    console.print("[bold magenta]=== LM Studio Telegram Bot Launcher ===[/bold magenta]")

    models = list_models()
    if not models:
        console.print("[red]No models found in LM Studio![/red]")
        exit()

    model = choose_model(models)
    gpu_index, gpu_name = choose_gpu()

    lm = launch_lmstudio(model, gpu_index)
    ngrok_url = launch_ngrok()
    api = launch_fastapi()

    set_webhook(ngrok_url)

    console.print("\n[bold green]System running! Press CTRL+C to stop everything.[/bold green]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        lm.terminate()
        api.terminate()
        console.print("[green]All processes stopped.[/green]")
