import os
import threading
from datetime import datetime
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask

app = Flask(__name__)

XAI_API_KEY = os.getenv("XAI_API_KEY")
PRIVATE_WEBHOOK = os.getenv("DISCORD_PRIVATE_WEBHOOK")
PUBLIC_WEBHOOK = os.getenv("DISCORD_PUBLIC_WEBHOOK")

# === YOUR FULL V6.3 PROMPT (paste the entire block) ===
NBA_PROMPT =  """**GROK DAILY NBA MULTI-PROP BETTING DIGEST TASK (2025-26 SEASON) – GROK-ONLY EXECUTION – VERSION 6.3 (FINAL OPTIMIZED)**

Generate the definitive daily NBA player and team props betting digest for TODAY’S DATE (YYYY-MM-DD) covering all games on the slate. This is a predictive, entertainment-oriented tool built exclusively on public data via Grok-native tools. It incorporates every validated enhancement from OnBall%, WOWY, Lineup Synergies, Pace Adjustment, and DvP for maximum repeatable edge.

**Prop Categories (Seven Dedicated Sections – No Overlap or Redundancy)**
1. Points Props
2. Rebounds Props
3. Assists Props
4. 3-Pointers Made Props
5. PRA Props
6. Double-Double / Triple-Double Props
7. Team Props (Team Total Points Per Quarter + Game Total Over/Under)

**Core Constraints & Execution Workflow (Fully Automated)**
- Slate Confirmation: browse_page(nba.com/schedule?date=YYYY-MM-DD) or espn.com/nba/schedule/_/date/YYYYMMDD; fallback web_search + basketball-reference.com.
- Social Signals: x_keyword_search on verified panel (@PropBomb, @CodyBrownBets, @vsaaauce, @ThePropAnt, @925_Sports, @homerunpredict, @FanDuelResearch, @TPB_NBAProps, @AngeloProps, @propsdotcash, @Stuckey2, @KBProps) since 03:00 ET. Secondary: x_keyword_search("#NBAProps OR #PlayerProps OR #NBAPlayerProps min_faves:50 since:YYYY-MM-DD"). x_semantic_search for sharp consensus.
- Image Validation: view_image on all media URLs (especially @homerunpredict graphics, lineup cards, projection tables). Extract and weight probabilities/tables.
- Lineups / Injuries / Projected Minutes: browse_page(rotowire.com/nba/daily-lineups, nba.com, fantasypros.com/injuries).
- Odds: browse_page(FanDuel, DraftKings, Bet365, Caesars, bettingpros.com/nba/props, covers.com/nba/player-props). Auto line-shop across minimum four books → record “Best Odds Shopped”.
- Metrics: nba.com/stats, basketball-reference.com, cleaningtheglass.com, databallr.com (OnBall%, WOWY, Stat Line Shift, Matchup Matrix) + L10 rolling.
- **Mandatory Databallr Extraction (every run)**: browse_page on https://databallr.com/wowy (league and key lineups), https://databallr.com/StatLineShift (player-specific), https://databallr.com/matchups (primary matchups), and relevant player/team dashboard pages. Extract and weight OnBall%, WOWY differentials, synergies, Stat Line Shift.
- Model Execution: code_execution for ensemble regression (Poisson for scoring/3PM, usage/DvP/WOWY regression for PRA/doubles). Report RMSE/MAE from 2025-26 backtest. Derive Model Prob % (weighted: BettingPros/Covers 30%, social-verified + view_image 30%, L10/BvP/WOWY/synergies/databallr 40% when full data extracted).

**Power-Value Score (Max 40 per Prop – Tailored Thresholds)**
**Base Metrics (0–30)** – Customized per category
- Points / 3PM: L10 vs line (8/6/4/2), Season avg adj (6/4/2/1), Opp Def to Pos (8/6/4/-1), Usage L10 (+3/2/1), Min proj (+3/2/1), Streak (+3/2/1), Edge (+2)
- Rebounds / Assists: Analogous with rebound/assist rate emphasis
- PRA / Double-Double / Triple-Double: L10 combo vs line, season PRA avg, opp defensive metrics, usage, minutes, streak, BvP, @homerunpredict projection boost (+2 if verified via view_image)

**Environmental & Market Bonuses (max +10)**
- Rest / No B2B: +2
- Pace / matchup boost: +1–2 (Pace Delta validated)
- Injury / usage edge: +1
- Efficiency L10: +1
- BvP strong: +1
- Market inefficiency (≥18% delta after line shopping): +4
- Social consensus (1 pt per verified account, max +4; +0.5 per high-engagement hashtag post, max +2)
- Sentiment Boost (max +2): +1 for ≥3 sharp mentions; +1 for positive Reddit consensus (web_search site:reddit.com/r/sportsbook OR r/nba)
- OnBall% / WOWY / Synergy Edge: +2 (databallr-validated usage/WOWY differential ≥+5 net rating or ≥5% OnBall%/usage spike)
- DvP Edge: +2 to +4 (opponent ranks top-8 worst vs player’s primary position)

**Thresholds**
- Valid Pick: ≥20
- Lock: ≥26 + streak + BvP
- Consensus Lock: ≥3 sources align (social + view_image)
- Value: Odds >+150 (or strong Under) & ≥20
- Longshot: 16–19 & odds ≥+200 (or alt lines)

**Output Structure**
**NBA Player Props Digest – [TODAY’S DATE] (Full Slate)**
**Overall Play of the Day / Value of the Day / Top Locks / Consensus Locks** (top 3–4 across all categories)

**1. Points Props**
| Player | Team | Opponent | Line | Side | Odds | Best Odds Shopped | Proj Min / OnBall% | Pace Delta | Opp DvP Rank | Score | Model Prob % | EV % | Projected Edge % | Sources | Tags | Notes |
(Same columns for Rebounds, Assists, 3-Pointers Made, PRA, Double-Double / Triple-Double)

**7. Team Props**
| Team | Opponent | Quarter / Game | Line | Side | Odds | Best Odds Shopped | Pace Delta | Score | Model Prob % | EV % | Projected Edge % | Sources | Tags | Notes |

**Databallr Advanced Insights**
| Player | Key Metric | Value | Edge vs League Avg | Impact on Score | Notes |

**Alt Line & Ladder Highlights** (across all player prop categories)
| Player | Category | Alt Line / Ladder | Side | Odds | Best Odds Shopped | Score | Model Prob % | EV % | Projected Edge % | Sources | Tags | Notes |
(Include only legs with EV ≥+0.21 and Score ≥20, e.g., 3PM ladders, Rebounds ladders, Assists ladders, PRA ladders, etc.)

**Notes** (per section, ≤50 words): Top 3 drivers + summary sentence. Include sentiment consensus, “OnBall% Spike Alert”, “WOWY / Synergy Alert”, “Pace-Up/Down Alert”, “DvP Edge Alert”, “High-EV Ladder Alert” where applicable.

**Slate Projection Footer**
Projected hits from Score ≥20: X.X–X.X (10,000-iteration Monte Carlo ensemble via code_execution; simulated hit rate XX%).

**Correlated Stacks / Same-Game Parlay Note**
Recommended SGPs with combined model prob and EV (include ladders/alt lines only when EV ≥+0.21).

**Historical Performance (YTD)**
2025-26 hit rate on Score ≥20 / ROI by category / avg CLV (updated weekly via code_execution).

**Data Sources Used (Transparency Footer)**
- Exact x_keyword_search / x_semantic_search queries + qualifying posts summary
- view_image extractions (tables/probabilities)
- code_execution regression output (RMSE/MAE, ensemble weights)
- databallr.com (OnBall%, WOWY, synergies, Stat Line Shift, Matchup Matrix) with specific pages accessed, cleaningtheglass.com, hashtagbasketball.com / bettingpros.com (DvP), basketball-reference.com (pace), primary odds/metrics sites with exact timestamps (post-03:00 ET)

**Tag Legend**
✅ Valid 💰 Value 🎯 Play of the Day 🔒 Lock Consensus Lock 🟢 Environment 🌐 Market Edge 🌪️ Arbitrage

**Deliverables**
- Top tables only (Score ≥20, sorted descending by Score)
- Play of the Day / Value of the Day / Locks / Longshots / Alt-Line highlights
- Databallr Advanced Insights
- Alt Line & Ladder Highlights
- Correlated stacks
- Full disclaimer + bankroll guidance (0.5–1.0% per core pick, Kelly capped at 25% of edge)

**No-Pick Scenario**: “No confident picks today” if none ≥20.

**Disclaimer**
This is a predictive, entertainment-oriented tool based on public data and model estimates. It is not financial advice. Always verify current odds and lineups. Gamble responsibly: 18+. Responsible gambling resources at rg.org.

**Version 6.3 Notes (All Additions & Revisions)**
- Maximum Databallr utilization on every run with explicit page targets, increased model weighting (40%), and dedicated output subsection.
- Full systematic Alt Line & Ladder Highlights across all categories (Points, Rebounds, Assists, 3PM, PRA, Doubles).
- Full alignment with CBB V5.0 / Soccer V3.0 / PGA V6.1 / UFC V5.0.
- Projected impact: 60–67% hit rate on valid picks, +0.22 avg EV.
- This is the complete, final, locked master task prompt. It represents the absolute maximum edge achievable with public data and Grok-native tools."""

def call_grok(prompt, date_str):
    headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "grok-4", "messages": [{"role": "user", "content": prompt.replace("TODAY’S DATE", date_str)}], "temperature": 0.3}
    resp = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers, timeout=180)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def split_message(text, max_length=1900):
    """Split long messages for Discord"""
    chunks = []
    current = ""
    for line in text.split('\n'):
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current)
            current = line
        else:
            current += "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks

def send_to_discord(webhook, content, title):
    chunks = split_message(content)
    for i, chunk in enumerate(chunks):
        prefix = f"**{title} - {datetime.now().strftime('%Y-%m-%d %H:%M ET')} (Part {i+1}/{len(chunks)})**\n\n"
        payload = {"content": prefix + chunk}
        requests.post(webhook, json=payload, timeout=10)

def run_nba():
    today = datetime.now().strftime("%Y-%m-%d")
    full_digest = call_grok(NBA_PROMPT, today)
    send_to_discord(PRIVATE_WEBHOOK, full_digest, "NBA Internal Full Digest (All Sources)")
    public_digest = full_digest.replace("databallr.com", "advanced analytics").replace("@PropBomb", "sharp social consensus")
    send_to_discord(PUBLIC_WEBHOOK, public_digest, "NBA Public Digest")

# Run immediately on startup for testing
run_nba()

# Daily scheduler at 10:00 AM ET
def start_scheduler():
    scheduler = BlockingScheduler(timezone="US/Eastern")
    scheduler.add_job(run_nba, 'cron', hour=10, minute=0)
    scheduler.start()

threading.Thread(target=start_scheduler, daemon=True).start()

@app.route("/")
def home():
    return "Sports Digest Scheduler is running..."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
