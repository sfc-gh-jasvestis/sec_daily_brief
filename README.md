# Daily Cybersecurity Brief

An automated n8n workflow system that generates comprehensive daily cybersecurity intelligence briefs from multiple RSS sources, with AI-powered categorization and a modern Streamlit dashboard.

## 🔒 Features

- **Automated Collection**: Monitors 13 premium security RSS feeds
- **AI Categorization**: GPT-4o powered story categorization across 17 security domains
- **Smart Deduplication**: Filters duplicate stories across 7-day history and non-English content
- **Historical Archive**: 7-day rolling history with date-based browsing
- **Website Source Display**: See the source website for each story
- **Singapore Timezone**: All timestamps displayed in SGT
- **Enhanced Navigation**: Filter by category or threat level groups
- **Dark Theme**: Modern, responsive UI optimized for security professionals

## 📊 Categories

### 🚨 Critical Threats
- Zero-Day Exploits
- Threat Intelligence & APTs
- Breaches/Ransomware

### 🛡️ Vulnerabilities & Defense
- Vulnerabilities
- Incident Response & Forensics
- Identity & Access Management

### 🏢 Enterprise & Infrastructure
- Supply Chain Security
- Cloud/SaaS
- Critical Infrastructure & OT/ICS
- Mobile & IoT Security

### 📋 Governance & Business
- Policy/Regulation
- Data Privacy & Protection
- Compliance & Audit

### 💡 Innovation & Insights
- Security Operations & Tools
- Startups/Funding
- Research
- AI/ML

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- n8n (Docker recommended)
- OpenAI API key

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
- Configure OpenAI credentials

4. **Start the system**
```bash
python start_history_system.py
```

### Access Points

- **Streamlit Dashboard**: http://localhost:8501
- **Webhook Server**: http://localhost:8080
- **n8n UI**: http://localhost:5678

## 📁 Project Structure

```
.
├── My workflow.json              # n8n workflow definition
├── streamlit_history_app.py      # Streamlit dashboard with history
├── webhook_streamlit_server_history.py  # Flask webhook server
├── start_history_system.py       # System launcher
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### Workflow Schedule

The workflow runs daily at **10 AM Singapore Time** (configurable in `My workflow.json`).

### RSS Sources

Currently monitoring 13 security sources including:
- Bleeping Computer
- The Hacker News
- Dark Reading
- Security Week
- CSO Online
- The Register
- Krebs on Security
- And more...

### AI Model

- **Model**: GPT-4o
- **Max Tokens**: 16,000
- **Story Target**: 20-30 stories per brief
- **Categories**: 17 comprehensive security categories
- **Deduplication**: Automatic filtering of duplicate URLs and non-English content

## 📱 Usage

### Browse Current Brief

1. Open http://localhost:8501
2. View today's brief with all stories
3. Use filters to focus on specific categories or threat levels

### Filter by Category

1. Click **"📁 By Category"** tab
2. Select a category from the dropdown
3. View filtered stories

### Filter by Threat Level

1. Click **"🎯 By Threat Level"** tab
2. Click a threat level button (Critical, Defense, Enterprise, etc.)
3. View stories in that threat group

### Browse History

1. Use the sidebar **"📅 Select Date"** dropdown
2. Choose a date from the last 7 days (shows "Today", "Yesterday", or "X days ago")
3. View historical briefs with automatic deduplication

## 🔄 Workflow Details

### Data Flow

1. **RSS Collection**: 13 feeds polled daily at 10 AM SGT
2. **AI Processing**: GPT-4o categorizes and summarizes stories
3. **Webhook Delivery**: n8n sends processed data to Flask webhook server
4. **Smart Filtering**: 
   - Removes duplicate URLs from previous 7 days
   - Filters non-English stories automatically
   - Sanitizes HTML tags from content
5. **Storage**: Webhook server saves current + 7-day historical files
6. **Display**: Streamlit dashboard with category filters and date navigation

### Error Handling

- JSON parsing errors are caught and displayed
- Truncated responses detected with diagnostic info
- Empty categories gracefully handled
- File storage failures logged

## 🎨 Customization

### Adjust Categories

Edit the AI prompt in `My workflow.json` (line ~167):
```javascript
"categories": ["Category1", "Category2", ...]
```

### Change Schedule

Edit the Schedule Trigger in `My workflow.json`:
```json
"triggerAtHour": 10,  // Change hour
"timezone": "Asia/Singapore"  // Change timezone
```

### Modify Story Count

Edit AI prompt target:
```
"Include 20-30 stories" → "Include X-Y stories"
```

## 📊 Data Format

Stories are saved in JSON format:
```json
{
  "title": "Daily Cybersecurity Brief",
  "total_stories": 11,
  "categories": [...],
  "stories": [
    {
      "category": "Vulnerabilities",
      "headline": "...",
      "summary": "...",
      "why_matters": "...",
      "companies": [...],
      "url": "...",
      "published_date": "2025-10-20T09:49:00Z"
    }
  ],
  "metadata": {
    "source": "13 Security Sources",
    "ai_model": "GPT-4o",
    "last_update": "2025-10-20T12:00:00Z",
    "workflow_version": "7.1"
  },
  "deduplication": {
    "original_count": 17,
    "duplicate_count": 6,
    "non_english_count": 0,
    "new_stories_count": 11,
    "previously_seen_urls": 134
  },
  "generated_at": "2025-10-20T10:01:03.918Z",
  "singapore_date": "Monday, 20 October 2025"
}
```

## 🛠️ Troubleshooting

### Workflow fails with JSON parsing error

1. Check debug logs in n8n execution
2. Verify maxTokens is sufficient (16000+)
3. Reduce story count target if needed

### No stories showing

1. Verify RSS feeds are accessible
2. Check date filtering logic
3. Ensure webhook server is running

### Category filtering not working

1. Clear browser cache (Ctrl+Shift+R)
2. Click "🔄 Refresh Data" in sidebar
3. Check category names match exactly

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with**: n8n, Streamlit, Flask, OpenAI GPT-4o, Python, Love for Security ❤️
