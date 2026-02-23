import os
import threading
from datetime import datetime
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask

app = Flask(__name__)

# Load prompt from separate file (safer for long prompt)
with open("nba_prompt.txt", "r", encoding="utf-8") as f:
    NBA_PROMPT = f.read()

print("✅ Prompt loaded successfully")

XAI_API_KEY = os.getenv("XAI_API_KEY")
PRIVATE_WEBHOOK = os.getenv("DISCORD_PRIVATE_WEBHOOK")
PUBLIC_WEBHOOK = os.getenv("DISCORD_PUBLIC_WEBHOOK")

def call_grok(prompt, date_str):
    try:
        headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "grok-4", "messages": [{"role": "user", "content": prompt.replace("TODAY’S DATE", date_str)}], "temperature": 0.3}
        resp = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return f"API Error: {str(e)}"

def redact_for_public(text):
    redacted = text.replace("databallr.com", "advanced analytics")
    redacted = redacted.replace("@PropBomb", "sharp social consensus")
    # Add more replacements if you see specific handles in logs
    return redacted

def send_to_discord(webhook, content, title):
    payload = {"content": f"**{title} - {datetime.now().strftime('%Y-%m-%d %H:%M')}**\n\n{content[:1900]}"}
    try:
        requests.post(webhook, json=payload, timeout=10)
        print(f"✅ Sent to Discord: {title}")
    except Exception as e:
        print(f"❌ Discord send error: {str(e)}")

def run_nba():
    print("🚀 Running NBA digest now...")
    today = datetime.now().strftime("%Y-%m-%d")
    full_digest = call_grok(NBA_PROMPT, today)
    
    # Internal full version
    send_to_discord(PRIVATE_WEBHOOK, full_digest, "NBA Internal Full Digest")
    
    # Public redacted version
    public_digest = redact_for_public(full_digest)
    send_to_discord(PUBLIC_WEBHOOK, public_digest, "NBA Public Digest")
    
    print("✅ NBA digest completed and posted at", datetime.now())

# Run immediately on startup (for testing)
print("🔄 Running immediate test digest...")
run_nba()

# Scheduler for daily 10 AM ET
def start_scheduler():
    scheduler = BlockingScheduler(timezone="US/Eastern")
    scheduler.add_job(run_nba, 'cron', hour=10, minute=0)
    print("⏰ Scheduler started – next run at 10:00 AM ET daily")
    scheduler.start()

# Start scheduler in background
threading.Thread(target=start_scheduler, daemon=True).start()

# Keep-alive server for Render
@app.route("/")
def home():
    return "Sports Digest Scheduler is running... (last check: " + datetime.now().strftime("%H:%M") + ")"

@app.route("/run")
def manual_run():
    run_nba()
    return "NBA digest triggered manually – check Discord!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
