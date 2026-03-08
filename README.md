# Daily Cybersecurity Brief

An automated n8n workflow system that generates comprehensive daily cybersecurity intelligence briefs from multiple RSS sources, with AI-powered categorization, severity scoring, and a modern Streamlit dashboard.

## Features

- **Automated Collection**: Monitors 21 premium security RSS feeds
- **Feed Health Monitoring**: Logs per-feed item counts and flags stale/dead feeds
- **AI Categorization**: Gemini 3.1 Pro powered story categorization across 17 security domains
- **Severity Scoring**: Each story scored 1-5 (Critical, High, Medium, Low, Info)
- **Pre-AI Deduplication**: URL and title-similarity dedup before sending to AI, saving ~20-30% tokens
- **Smart Deduplication**: Cross-day dedup filters duplicate stories across 7-day history
- **Historical Archive**: 7-day rolling history with date-based browsing
- **Search**: Full-text search across headlines, summaries, companies, and CVEs
- **Trend Charts**: 7-day story volume, category breakdown, and severity distribution
- **Website Source Display**: See the source website for each story
- **Singapore Timezone**: All timestamps displayed in SGT
- **Dark Theme**: Modern, responsive UI optimized for security professionals

## Categories

### Critical Threats
- Zero-Day Exploits
- Threat Intelligence & APTs
- Breaches/Ransomware

### Vulnerabilities & Defense
- Vulnerabilities
- Incident Response & Forensics
- Identity & Access Management

### Enterprise & Infrastructure
- Supply Chain Security
- Cloud/SaaS
- Critical Infrastructure & OT/ICS
- Mobile & IoT Security

### Governance & Business
- Policy/Regulation
- Data Privacy & Protection
- Compliance & Audit

### Innovation & Insights
- Security Operations & Tools
- Startups/Funding
- Research
- AI/ML

## Severity Scores

Each story is assigned a severity score by the AI:

| Score | Label | Meaning |
|-------|-------|---------|
| 5 | CRITICAL | Active exploitation, zero-day, major breach |
| 4 | HIGH | Significant vulnerability, large-scale attack |
| 3 | MEDIUM | Notable security event, new threat actor activity |
| 2 | LOW | Policy update, research finding, tool release |
| 1 | INFO | Funding news, opinion, minor update |

## Schedule

| Trigger | Time | Purpose |
|---------|------|---------|
| Morning run | 10:00 AM SGT | Catch overnight + Asia-Pacific news |
| Evening run | 6:00 PM SGT | Catch US morning news cycle |

## Quick Start

### Prerequisites

- Python 3.8+
- n8n (Docker recommended)
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sfc-gh-jasvestis/sec_daily_brief.git
cd sec_daily_brief
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Import n8n workflow**
- Start n8n: `docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n`
- Import `My workflow.json` via the n8n UI
- Add a **Google Gemini(PaLM)** credential in n8n with your Gemini API key
- Connect the credential to the `Message a model` node
4. **Start the system**
```bash
python start_history_system.py
```

### Access Points

- **Streamlit Dashboard**: http://localhost:8501
- **Webhook Server**: http://localhost:8080
- **n8n UI**: http://localhost:5678

## Project Structure

```
.
├── My workflow.json                      # n8n workflow definition
├── streamlit_history_app.py              # Streamlit dashboard with history, search, trends
├── webhook_streamlit_server_history.py   # Flask webhook server with dedup + seen-URLs API
├── start_history_system.py               # System launcher
├── requirements.txt                      # Python dependencies
├── history/                              # 7-day rolling history files
└── README.md
```

## Workflow Pipeline

```
Schedule Trigger (10 AM) ──→ 26 RSS Feeds ──→ Merge
Schedule Trigger (6 PM) ───→ 26 RSS Feeds ──→ Merge
                                                ↓
                                     Feed Health Check (log per-feed stats, flag stale feeds)
                                                ↓
                                     Limit (400 items max)
                                                ↓
                                     Prepare Stories (date filter + URL dedup + title dedup + language filter)
                                                ↓
                                     Gemini 3.1 Pro Analysis (categorize + summarize + severity score)
                                                ↓
                                     Process and Save (parse JSON, validate severity, post-AI dedup)
                                                ↓
                                     Save to Webhook
                                                ↓
                                     Workflow Complete
```

## Dashboard Features

### Browse Current Brief
1. Open http://localhost:8501
2. View today's brief with severity badges on each story
3. Critical/High stories are visually highlighted

### Filter by Severity
1. Click the **"By Severity"** tab
2. Click a severity button (🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low, ⚪ Info)
3. Active filter shows count of matching stories

### View Trends
1. Click the **"Trends"** tab
2. See daily story volume over the last 7 days
3. See category breakdown stacked by day
4. See severity distribution over time (spikes in Critical/High are notable)

### Browse History
1. Use the sidebar **"Select Date"** dropdown
2. Choose from the last 7 days

## API Endpoints (Webhook Server)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhook/tech-brief` | POST | Receive processed brief from n8n |
| `/api/seen-urls` | GET | Return all story URLs from last 7 days (for pre-AI dedup) |
| `/api/history` | GET | List available historical dates |
| `/api/history/<date>` | GET | Get brief for a specific date |
| `/health` | GET | Health check |

## Configuration

### AI Model
- **Model**: Gemini 3.1 Pro
- **Max Output Tokens**: 28,000
- **Temperature**: 0.2 (consistent JSON output)
- **Story Target**: 40-60 stories per brief
- **Categories**: 17 comprehensive security categories
- **Severity Scores**: 1-5 per story

### RSS Sources (21)
- Bleeping Computer
- The Hacker News
- Dark Reading
- Security Week
- Krebs on Security
- CSO Online
- The Register
- Wired Security
- ESET Blog
- Schneier on Security
- Techcrunch
- Microsoft Security
- Google Security
- AWS Security
- Cisco Talos
- Unit 42
- CISA Alerts
- CrowdStrike
- Tenable
- SANS ISC
- Malwarebytes

## Troubleshooting

### Workflow fails with JSON parsing error
1. Check debug logs in n8n execution
2. maxOutputTokens is set to 28,000 — increase further if needed
3. Reduce story count target if needed

### No stories showing
1. Check Feed Health Check logs for stale/dead feeds
2. Verify RSS feeds are accessible
3. Ensure webhook server is running

## Data Format

Stories are saved in JSON format with severity scores:
```json
{
  "title": "Daily Cybersecurity Brief",
  "total_stories": 28,
  "categories": [...],
  "stories": [
    {
      "category": "Zero-Day Exploits",
      "headline": "...",
      "summary": "...",
      "why_matters": "...",
      "severity": 5,
      "companies": [...],
      "url": "...",
      "published_date": "2026-02-18T09:49:00Z"
    }
  ],
  "metadata": {
    "source": "26 Security Sources",
    "ai_model": "Gemini 3.1 Pro",
    "last_update": "2026-02-18T10:00:00Z",
    "workflow_version": "8.0"
  },
  "deduplication": {
    "original_count": 33,
    "duplicate_count": 5,
    "non_english_count": 0,
    "new_stories_count": 28,
    "previously_seen_urls": 131
  }
}
```

---

**Built with**: n8n, Streamlit, Flask, Google Gemini 3.1 Pro, Plotly, Python
