import os
import threading
from datetime import datetime
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask

app = Flask(__name__)

# === CONFIG ===
XAI_API_KEY = os.getenv("XAI_API_KEY")
PRIVATE_WEBHOOK = os.getenv("DISCORD_PRIVATE_WEBHOOK")
PUBLIC_WEBHOOK = os.getenv("DISCORD_PUBLIC_WEBHOOK")

# === YOUR FULL NBA V6.3 PROMPT HERE ===
NBA_PROMPT = """**GROK DAILY NBA MULTI-PROP BETTING DIGEST TASK (2025-26 SEASON) – GROK-ONLY EXECUTION – VERSION 6.3 (FINAL OPTIMIZED)** 
... [PASTE THE ENTIRE V6.3 PROMPT YOU COPIED FROM OUR LAST MESSAGE] ..."""

def call_grok(prompt, date_str):
    headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "grok-4", "messages": [{"role": "user", "content": prompt.replace("TODAY’S DATE", date_str)}], "temperature": 0.3}
    resp = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
    return resp.json()["choices"][0]["message"]["content"]

def redact_for_public(text):
    redacted = text.replace("databallr.com", "advanced analytics")
    redacted = redacted.replace("@PropBomb", "sharp social consensus")
    # Add more replacements later if needed
    return redacted

def send_to_discord(webhook, content, title):
    payload = {"content": f"**{title} - {datetime.now().strftime('%Y-%m-%d')}**\n\n{content[:1900]}"}
    requests.post(webhook, json=payload)

def run_nba():
    today = datetime.now().strftime("%Y-%m-%d")
    full_digest = call_grok(NBA_PROMPT, today)
    
    # Internal full version
    send_to_discord(PRIVATE_WEBHOOK, full_digest, "NBA Internal Full Digest")
    
    # Public redacted version
    public_digest = redact_for_public(full_digest)
    send_to_discord(PUBLIC_WEBHOOK, public_digest, "NBA Public Digest")
    print(f"NBA digest completed and posted at {datetime.now()}")

# === SCHEDULER (runs in background thread) ===
def start_scheduler():
    scheduler = BlockingScheduler(timezone="US/Eastern")
    scheduler.add_job(run_nba, 'cron', hour=10, minute=0)  # 10:00 AM ET daily
    scheduler.start()

# === KEEP-ALIVE WEB SERVER (required by Render) ===
@app.route("/")
def home():
    return "Sports Digest Scheduler is running..."

if __name__ == "__main__":
    # Start scheduler in background
    threading.Thread(target=start_scheduler, daemon=True).start()
    # Start Flask server on Render's required port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
