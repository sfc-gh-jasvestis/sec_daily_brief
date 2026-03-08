# Daily Cybersecurity Brief

An automated n8n workflow system that generates comprehensive daily cybersecurity intelligence briefs from 21 RSS sources, with AI-powered categorisation, severity scoring, and a modern Streamlit dashboard — all running in Docker.

## Features

- **Automated Collection**: Monitors 21 premium security RSS feeds twice daily
- **Feed Health Monitoring**: Logs per-feed item counts and flags stale/dead feeds
- **AI Categorisation**: Gemini 3.1 Pro Preview powered story categorisation across 17 security domains
- **Severity Scoring**: Each story scored 1–5 (Critical → Info)
- **3-Layer Deduplication**: URL dedup → title-similarity dedup → post-AI dedup removes cross-site duplicates
- **Historical Archive**: 7-day rolling history with date-based browsing
- **Trend Charts**: 7-day story volume, category breakdown, and severity distribution
- **Singapore Timezone**: All timestamps displayed in SGT
- **Dark Theme**: Modern, responsive UI optimised for security professionals

## Categories

### Critical Threats
- Zero-Day Exploits
- Threat Intelligence & APTs
- Breaches/Ransomware

### Vulnerabilities & Defence
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

- Docker + Docker Compose
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sfc-gh-jasvestis/sec_daily_brief.git
cd sec_daily_brief
```

2. **Add your Gemini API key** to `docker-compose.yml`:
```yaml
environment:
  GEMINI_API_KEY: your_api_key_here
```

3. **Start all services**
```bash
docker compose up -d
```

4. **Import the n8n workflow**
- Open http://localhost:5678
- Import `My workflow.json` via the n8n UI (no credentials needed — the API key is read from the environment variable)

### Access Points

- **Streamlit Dashboard**: http://localhost:8501
- **Webhook Server**: http://localhost:8080
- **n8n UI**: http://localhost:5678

## Project Structure

```
.
├── My workflow.json                      # n8n workflow definition
├── streamlit_history_app.py              # Streamlit dashboard
├── webhook_streamlit_server_history.py   # Flask webhook server
├── requirements.txt                      # Python dependencies
├── docker-compose.yml              # Docker Compose (SQLite, no PostgreSQL)
├── Dockerfile.n8n                        # n8n container
├── Dockerfile.webhook                    # Webhook server container
├── Dockerfile.streamlit                  # Streamlit container
├── history/                              # 7-day rolling history files
└── README.md
```

## Workflow Pipeline

```
Schedule Trigger (10 AM SGT) ──→ 21 RSS Feeds ──→ Merge
Schedule Trigger  (6 PM SGT) ──→ 21 RSS Feeds ──→ Merge
                                                    ↓
                                         Feed Health Check
                                         (log per-feed stats, flag stale feeds)
                                                    ↓
                                         Limit (600 items max)
                                                    ↓
                                         Prepare Stories
                                         (date filter → URL dedup → title dedup → language filter)
                                                    ↓
                                         Build Gemini Request
                                         (trim to 150 stories, 200-char snippets, build API body)
                                                    ↓
                                         Call Gemini API (gemini-3.1-pro-preview)
                                         (categorise + summarise + severity score)
                                                    ↓
                                         Process and Save
                                         (parse JSON, validate severity, post-AI URL dedup)
                                                    ↓
                                         Save to Webhook → Streamlit Dashboard
```

## Deduplication (3 Layers)

| Layer | Node | What it catches |
|-------|------|-----------------|
| 1 | Prepare Stories | Exact URL match (strips query params) + normalised title match (first 60 alphanum chars) |
| 2 | Gemini prompt | Semantic duplicates — same story from different sites with different wording |
| 3 | Process and Save | Exact URL match on Gemini's output — catches any re-introduced duplicates |

## Dashboard Features

### Browse Current Brief
1. Open http://localhost:8501
2. View today's brief with severity badges on each story
3. Critical/High stories are visually highlighted

### Filter by Severity
- Click a severity button: 🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low, ⚪ Info
- Shows count of matching stories for the active filter

### View Trends
- See daily story volume over the last 7 days
- Category breakdown and severity distribution over time

### Browse History
- Use the sidebar **"Select Date"** dropdown to browse the last 7 days

## API Endpoints (Webhook Server)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhook/tech-brief` | POST | Receive processed brief from n8n |
| `/api/seen-urls` | GET | Return all story URLs from last 7 days (for dedup) |
| `/api/history` | GET | List available historical dates |
| `/api/history/<date>` | GET | Get brief for a specific date |
| `/health` | GET | Health check |

## Configuration

### AI Model
- **Model**: `gemini-3.1-pro-preview`
- **Max Output Tokens**: 28,000
- **Temperature**: 0.2 (consistent, deterministic JSON output)
- **Timeout**: 300 seconds
- **Story Target**: 40–60 stories per brief
- **API Key**: Set `GEMINI_API_KEY` in `docker-compose.yml`

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

### Timeout error on Call Gemini API
- Check the `Build Gemini Request` node logs to see how many stories were sent
- Reduce `slice(0, 150)` further (e.g. `100`) in the Build Gemini Request node if timeouts persist
- Gemini 3.1 Pro Preview can take 60–120 seconds for large payloads — this is normal

### Workflow fails with JSON parsing error
1. Check debug logs in the `Process and Save` node
2. `maxOutputTokens` is set to 28,000 — increase if briefs are being truncated
3. The error log will show the last 500 chars of the response to help diagnose

### No stories showing in dashboard
1. Check `Feed Health Check` logs in n8n for stale/dead feeds
2. Verify the webhook server is running: `curl http://localhost:8080/health`
3. Check n8n execution logs for errors in `Prepare Stories` (date filter may be too strict)

### GEMINI_API_KEY not found
- Ensure the key is set in `docker-compose.yml` under the `n8n` service environment
- Restart n8n after updating: `docker compose up -d --no-deps n8n`

## Data Format

```json
{
  "title": "Daily Cybersecurity Brief",
  "total_stories": 45,
  "categories": ["Zero-Day Exploits", "Breaches/Ransomware", "..."],
  "stories": [
    {
      "category": "Zero-Day Exploits",
      "headline": "...",
      "summary": "...",
      "why_matters": "...",
      "severity": 5,
      "companies": ["vendor"],
      "url": "https://...",
      "published_date": "2026-02-19T09:00:00Z"
    }
  ],
  "metadata": {
    "source": "21 Security Sources",
    "ai_model": "Gemini 3.1 Pro Preview",
    "last_update": "2026-02-19T10:00:00Z",
    "workflow_version": "8.0"
  }
}
```

---

**Built with**: n8n, Docker, Streamlit, Flask, Google Gemini 3.1 Pro Preview, Plotly, Python
