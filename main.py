import os
import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

XAI_API_KEY = os.getenv("XAI_API_KEY")
PRIVATE_WEBHOOK = os.getenv("DISCORD_PRIVATE_WEBHOOK")
PUBLIC_WEBHOOK = os.getenv("DISCORD_PUBLIC_WEBHOOK")

# === YOUR FULL NBA V6.3 PROMPT HERE (paste the entire block from our last message) ===
NBA_PROMPT = """**GROK DAILY NBA MULTI-PROP BETTING DIGEST TASK (2025-26 SEASON) – GROK-ONLY EXECUTION – VERSION 6.3 (FINAL OPTIMIZED)** 
... [PASTE THE ENTIRE V6.3 PROMPT YOU COPIED EARLIER] ..."""

def call_grok(prompt, date_str):
    headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "grok-4", "messages": [{"role": "user", "content": prompt.replace("TODAY’S DATE", date_str)}], "temperature": 0.3}
    resp = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
    return resp.json()["choices"][0]["message"]["content"]

def redact_for_public(text):
    redacted = text.replace("databallr.com", "advanced analytics")
    redacted = redacted.replace("@PropBomb", "sharp social consensus")
    # Add more replacements if needed (e.g., other handles)
    return redacted

def send_to_discord(webhook, content, title):
    payload = {"content": f"**{title} - {datetime.now().strftime('%Y-%m-%d')}**\n\n{content[:1900]}"}
    requests.post(webhook, json=payload)

def run_nba():
    today = datetime.now().strftime("%Y-%m-%d")
    full_digest = call_grok(NBA_PROMPT, today)
    
    # Internal (full sources)
    send_to_discord(PRIVATE_WEBHOOK, full_digest, "NBA Internal Full Digest")
    
    # Public (redacted, safe)
    public_digest = redact_for_public(full_digest)
    send_to_discord(PUBLIC_WEBHOOK, public_digest, "NBA Public Digest")

# Run every day at 10:00 AM ET (adjust hour if needed)
scheduler = BlockingScheduler(timezone="US/Eastern")
scheduler.add_job(run_nba, 'cron', hour=10, minute=0)
scheduler.start()
