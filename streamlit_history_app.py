#!/usr/bin/env python3
"""
Enhanced Streamlit app with 7-day history support for Daily Tech & Security Brief.
Shows current brief and allows browsing through the last 7 days of briefs.
"""

import streamlit as st
import json
import html
import os
import requests
from datetime import datetime, timedelta
import pytz
from typing import Dict, List
import glob
from urllib.parse import urlparse

# Configure Streamlit page
st.set_page_config(
    page_title="Daily Tech & Security Brief - History",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #64b5f6 0%, #90caf9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .brief-subtitle {
        text-align: center;
        color: #b0b0b0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .story-card {
        background: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        border-left: 4px solid #64b5f6;
        border: 1px solid #333;
        transition: transform 0.2s ease;
    }
    
    .story-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    .story-headline {
        font-size: 1.25rem;
        font-weight: bold;
        color: #90caf9;
        margin-bottom: 0.8rem;
    }
    
    .story-summary {
        color: #e0e0e0;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .why-matters {
        background: #2d2d2d;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #4caf50;
        margin-bottom: 1rem;
        font-style: italic;
        color: #e8f5e8;
    }
    
    .company-tag {
        background: #1565c0;
        color: #ffffff;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        display: inline-block;
    }
    
    .date-selector {
        background: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    
    .historical-indicator {
        background: #1a237e;
        color: #e3f2fd;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        border: 1px solid #3f51b5;
    }
    
    /* Sidebar styling fixes */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #2d2d44;
        color: #ffffff;
        border: 1px solid #4a4a6a;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #90caf9 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1565c0;
        color: white;
        border: none;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #1976d2;
    }
    
    /* Fix selectbox dropdown text */
    .stSelectbox [data-baseweb="select"] {
        background-color: #2d2d44;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: #2d2d44;
    }
    
    /* Fix info/warning boxes in sidebar */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #1e3a5f;
        color: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)

class HistoryTechBriefApp:
    def __init__(self):
        self.history_dir = "history"
        self.current_file = "tech_brief.json"
        self.webhook_url = "http://localhost:8080"
        
    def get_available_dates(self) -> List[str]:
        """Get available historical dates from local files"""
        if not os.path.exists(self.history_dir):
            return []
        
        pattern = os.path.join(self.history_dir, "tech_brief_*.json")
        dates = []
        
        for file_path in glob.glob(pattern):
            filename = os.path.basename(file_path)
            try:
                date_str = filename.replace('tech_brief_', '').replace('.json', '')
                # Validate date format
                datetime.strptime(date_str, '%Y-%m-%d')
                dates.append(date_str)
            except:
                continue
        
        # Sort dates in descending order (newest first)
        dates.sort(reverse=True)
        return dates
    
    def load_data_for_date(self, date: str = None) -> Dict:
        """Load data for specific date or current data"""
        try:
            if date:
                # Load historical data
                historical_file = os.path.join(self.history_dir, f"tech_brief_{date}.json")
                if os.path.exists(historical_file):
                    with open(historical_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    return {}
            else:
                # Load current data
                if os.path.exists(self.current_file):
                    with open(self.current_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    return {}
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return {}
    
    def format_singapore_time(self, timestamp: str, short_format: bool = False) -> str:
        """Format timestamp to Singapore timezone"""
        try:
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                singapore_tz = pytz.timezone('Asia/Singapore')
                singapore_time = dt.astimezone(singapore_tz)
                
                if short_format:
                    # Short format for metrics: "Sep 30, 15:30 SGT"
                    return singapore_time.strftime('%b %d, %H:%M SGT')
                else:
                    # Full format for story cards: "September 30, 2025 15:30 SGT"
                    return singapore_time.strftime('%B %d, %Y %H:%M SGT')
            return timestamp
        except:
            return timestamp
    
    def extract_domain(self, url: str) -> str:
        """Extract clean domain name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "Unknown source"
    
    def render_story_card(self, story: Dict):
        """Render a story card"""
        companies = story.get('companies', [])
        if isinstance(companies, str):
            companies = companies.split(',') if companies else []
        
        # Format published date
        pub_date = story.get('published_date', '')
        formatted_date = self.format_singapore_time(pub_date) if pub_date else 'Date not available'
        
        # Extract website domain
        url_raw = story.get('url', '#')
        website = self.extract_domain(url_raw)
        
        # Escape HTML to prevent rendering of tags in content
        headline = html.escape(story.get('headline', 'No headline available'))
        summary = html.escape(story.get('summary', 'No summary available'))
        why_matters = html.escape(story.get('why_matters', 'Analysis not available'))
        url = html.escape(url_raw)
        website_escaped = html.escape(website)
        
        # Build companies HTML separately
        companies_html = ''
        if companies and len(companies) > 0:
            company_tags = ' '.join([f'<span class="company-tag">{html.escape(company.strip())}</span>' for company in companies[:8] if company.strip()])
            if company_tags:
                companies_html = f'<div style="margin-top: 0.5rem;">{company_tags}</div>'
        
        severity = story.get('severity', 0)
        sev_badge = ''
        if severity and severity >= 1:
            sev_color_map = {5: '#d32f2f', 4: '#f57c00', 3: '#fbc02d', 2: '#42a5f5', 1: '#90a4ae'}
            sev_label_map = {5: 'CRITICAL', 4: 'HIGH', 3: 'MEDIUM', 2: 'LOW', 1: 'INFO'}
            sev_badge = f'<span style="background:{sev_color_map.get(severity,"#90a4ae")};color:#fff;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:bold;margin-right:8px">{sev_label_map.get(severity,"")}</span>'
            border_color = sev_color_map.get(severity, '#64b5f6')
        else:
            border_color = '#64b5f6'

        st.markdown(f"""<div class="story-card" style="border-left-color: {border_color};">
    <div class="story-headline">
        {sev_badge}<a href="{url}" target="_blank" style="text-decoration: none; color: #90caf9;">{headline}</a>
    </div>
    <div style="color: #b0b0b0; font-size: 0.9rem; margin-bottom: 0.8rem;">
        📅 {formatted_date} • 🌐 <a href="{url}" target="_blank" style="color: #64b5f6; text-decoration: none;">{website_escaped}</a>
    </div>
    <div class="story-summary">{summary}</div>
    <div class="why-matters"><strong>💡 Why it matters:</strong> {why_matters}</div>{companies_html}
</div>""", unsafe_allow_html=True)
    
    def render_date_selector(self) -> str:
        """Render date selector and return selected date"""
        available_dates = self.get_available_dates()
        
        if not available_dates:
            st.warning("No historical data available yet. Run your workflow to generate data.")
            return None
        
        # Create date options - only show actual dates
        date_options = [
            f"{date} ({self.format_date_display(date)})" 
            for date in available_dates
        ]
        
        selected_option = st.selectbox(
            "📅 Select Date",
            date_options,
            index=0,
            help="Choose which day's brief to view"
        )
        
        # Extract date from option string
        if selected_option is None or isinstance(selected_option, int):
            return available_dates[0] if available_dates else None
        return selected_option.split(' ')[0]
    
    def format_date_display(self, date_str: str) -> str:
        """Format date for display"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            today = datetime.now().date()
            date_date = date_obj.date()
            
            if date_date == today:
                return "Today"
            elif date_date == today - timedelta(days=1):
                return "Yesterday"
            else:
                days_ago = (today - date_date).days
                return f"{days_ago} days ago"
        except:
            return date_str
    
    def run(self):
        """Main app function"""
        # Header
        st.markdown('<h1 class="main-header">🔒 Daily Tech & Security Brief</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brief-subtitle">📊 Comprehensive Security Intelligence with 7-Day History</p>', unsafe_allow_html=True)
        
        # Sidebar for date selection
        with st.sidebar:
            st.header("📅 Browse History")
            selected_date = self.render_date_selector()
            
            # Show available dates info
            available_dates = self.get_available_dates()
            if available_dates:
                st.info(f"📁 {len(available_dates)} days of history available")
                
                # Show date range
                if len(available_dates) > 1:
                    oldest = available_dates[-1]
                    newest = available_dates[0]
                    st.caption(f"From {oldest} to {newest}")
            
            # Manual refresh
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        # Load data for selected date
        data = self.load_data_for_date(selected_date)
        
        if not data:
            st.error(f"No data found for {selected_date}")
            return
        
        # Show historical indicator only if viewing past data (not today)
        today_date = datetime.now().strftime('%Y-%m-%d')
        if selected_date and selected_date != today_date:
            singapore_date = data.get('singapore_date', selected_date)
            st.markdown(f"""
            <div class="historical-indicator">
                📚 Viewing Historical Brief: {singapore_date}
            </div>
            """, unsafe_allow_html=True)
        
        # Brief metadata
        metadata = data.get('metadata', {})
        
        # Summary metrics with responsive layout
        # Show deduplication info if available
        dedup_info = data.get('deduplication', {})
        duplicates = dedup_info.get('duplicate_count', 0)
        non_english = dedup_info.get('non_english_count', 0)
        has_filtering = duplicates > 0 or non_english > 0
        
        if has_filtering:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("New Stories Today", data.get('total_stories', 0))
            
            with col2:
                st.metric("Categories", len(data.get('categories', [])))
            
            with col3:
                st.metric("Duplicates Filtered", duplicates, 
                         help=f"Stories that appeared in previous days: {duplicates}")
            
            with col4:
                st.metric("Non-English Filtered", non_english,
                         help=f"Stories in other languages: {non_english}")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Stories", data.get('total_stories', 0))
            
            with col2:
                st.metric("Categories", len(data.get('categories', [])))
        
        # Generated time and source in full-width sections for better readability
        st.markdown("---")
        
        # Generated time section - prioritize generated_at over metadata last_update
        last_update = data.get('generated_at', '') or data.get('saved_at', '') or metadata.get('last_update', '')
        if last_update:
            time_str = self.format_singapore_time(last_update, short_format=True)
        else:
            time_str = 'Unknown'
        
        # Source section
        source = metadata.get('source', 'Unknown')
        
        # Display in a more readable format
        col_time, col_source = st.columns(2)
        with col_time:
            st.markdown(f"""
            <div style="background: #2d2d2d; padding: 1rem; border-radius: 8px; border-left: 4px solid #4caf50;">
                <div style="color: #b0b0b0; font-size: 0.8rem; margin-bottom: 0.3rem;">GENERATED AT</div>
                <div style="color: #e0e0e0; font-size: 1.1rem; font-weight: bold;">🕐 {time_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_source:
            st.markdown(f"""
            <div style="background: #2d2d2d; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3;">
                <div style="color: #b0b0b0; font-size: 0.8rem; margin-bottom: 0.3rem;">DATA SOURCE</div>
                <div style="color: #e0e0e0; font-size: 1.1rem; font-weight: bold; word-wrap: break-word; overflow-wrap: break-word;">📡 {source}</div>
            </div>
            """, unsafe_allow_html=True)

        # List RSS sources under Data Source for clarity
        rss_sources = [
            "Bleeping Computer",
            "The Hacker News",
            "Dark Reading",
            "Security Week",
            "Krebs on Security",
            "CSO Online",
            "The Register",
            "Wired Security",
            "ESET Blog",
            "Schneier on Security",
            "Techcrunch",
            "Microsoft Security",
            "Google Security",
            "AWS Security",
            "Cisco Talos",
            "Unit 42",
            "CISA Alerts",
            "CrowdStrike",
            "Tenable",
            "SANS ISC",
            "Malwarebytes"
        ]
        with st.expander("Sources", expanded=False):
            st.markdown("\n".join([f"- {src}" for src in rss_sources]))
        
        # Check if we have stories
        stories = data.get('stories', [])
        if not stories:
            st.warning("No stories available in this brief.")
            return
        
        # Severity summary bar removed for a cleaner header
        has_severity = any(s.get('severity') for s in stories)

        # Severity + trends controls
        st.markdown("---")
        st.markdown("### 🎯 Severity & Trends")
        
        # Create tabs for filter options
        severity_tab, trends_tab = st.tabs(["🎯 By Severity", "📈 Trends"])
        
        with severity_tab:
            if not has_severity:
                st.info("Severity filters are unavailable until severity scores exist.")
                selected_severity = 'All'
            else:
                # Count stories per severity level
                sev_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0, 0: 0}
                for story in stories:
                    sev = story.get('severity', 0)
                    if sev in sev_counts:
                        sev_counts[sev] += 1
                
                sev_labels = {5: 'CRITICAL', 4: 'HIGH', 3: 'MEDIUM', 2: 'LOW', 1: 'INFO', 0: 'UNSCORED'}
                sev_display = {
                    5: '🔴 CRITICAL',
                    4: '🟠 HIGH',
                    3: '🟡 MEDIUM',
                    2: '🔵 LOW',
                    1: '⚪ INFO',
                    0: '⚫ UNSCORED'
                }
                sev_order = [5, 4, 3, 2, 1]
                
                cols = st.columns(5)
                for idx, sev in enumerate(sev_order):
                    with cols[idx]:
                        if st.button(
                            f"{sev_display[sev]} ({sev_counts[sev]})",
                            use_container_width=True,
                            key=f"sev_{sev}"
                        ):
                            st.session_state['selected_severity'] = sev
                
                extra_cols = st.columns(1)
                with extra_cols[0]:
                    if sev_counts[0] > 0:
                        if st.button(
                            f"{sev_display[0]} ({sev_counts[0]})",
                            use_container_width=True,
                            key="sev_0"
                        ):
                            st.session_state['selected_severity'] = 0
                
                selected_severity = st.session_state.get('selected_severity', 'All')
                if selected_severity == 'All':
                    st.caption(f"Showing: All Severities ({len(stories)})")
                else:
                    st.caption(
                        f"Showing: {sev_labels.get(selected_severity, 'Unknown')} "
                        f"({sev_counts.get(selected_severity, 0)})"
                    )

        with trends_tab:
            available_dates = self.get_available_dates()
            if len(available_dates) < 2:
                st.info("Trend charts require at least 2 days of history. Keep running the workflow!")
            else:
                import plotly.graph_objects as go
                import plotly.express as px

                trend_data = []
                for d_str in sorted(available_dates):
                    hist = self.load_data_for_date(d_str)
                    if not hist:
                        continue
                    hist_stories = hist.get('stories', [])
                    cat_counts_hist = {}
                    sev_counts_hist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
                    for s in hist_stories:
                        cat = s.get('category', 'Other')
                        cat_counts_hist[cat] = cat_counts_hist.get(cat, 0) + 1
                        sv = s.get('severity', 3)
                        if sv in sev_counts_hist:
                            sev_counts_hist[sv] += 1
                    trend_data.append({
                        'date': d_str,
                        'total': len(hist_stories),
                        'categories': cat_counts_hist,
                        'severity': sev_counts_hist
                    })

                if trend_data:
                    dates = [t['date'] for t in trend_data]
                    totals = [t['total'] for t in trend_data]

                    # Total stories over time
                    fig_total = go.Figure()
                    fig_total.add_trace(go.Scatter(
                        x=dates, y=totals, mode='lines+markers',
                        line=dict(color='#64b5f6', width=3),
                        marker=dict(size=8), name='Total Stories'
                    ))
                    fig_total.update_layout(
                        title='Daily Story Volume', height=300,
                        paper_bgcolor='#0e1117', plot_bgcolor='#1a1a2e',
                        font_color='#e0e0e0', xaxis_title='', yaxis_title='Stories',
                        margin=dict(l=40, r=20, t=40, b=30)
                    )
                    st.plotly_chart(fig_total, use_container_width=True)

                    # Category breakdown over time (top 6)
                    all_cats_trend = set()
                    for t in trend_data:
                        all_cats_trend.update(t['categories'].keys())
                    cat_totals = {c: sum(t['categories'].get(c, 0) for t in trend_data) for c in all_cats_trend}
                    top_cats = sorted(cat_totals, key=lambda c: cat_totals[c], reverse=True)[:6]

                    cat_colors = ['#d32f2f', '#f57c00', '#fbc02d', '#42a5f5', '#66bb6a', '#ab47bc']
                    fig_cats = go.Figure()
                    for i, cat in enumerate(top_cats):
                        vals = [t['categories'].get(cat, 0) for t in trend_data]
                        fig_cats.add_trace(go.Bar(
                            x=dates, y=vals, name=cat,
                            marker_color=cat_colors[i % len(cat_colors)]
                        ))
                    fig_cats.update_layout(
                        title='Top Categories Over Time', barmode='stack', height=350,
                        paper_bgcolor='#0e1117', plot_bgcolor='#1a1a2e',
                        font_color='#e0e0e0', xaxis_title='', yaxis_title='Stories',
                        margin=dict(l=40, r=20, t=40, b=30),
                        legend=dict(orientation='h', y=-0.2)
                    )
                    st.plotly_chart(fig_cats, use_container_width=True)

                    # Severity distribution over time
                    any_sev = any(t['severity'].get(5, 0) + t['severity'].get(4, 0) > 0 for t in trend_data)
                    if any_sev:
                        sev_colors_chart = {5: '#d32f2f', 4: '#f57c00', 3: '#fbc02d', 2: '#42a5f5', 1: '#90a4ae'}
                        sev_names = {5: 'Critical', 4: 'High', 3: 'Medium', 2: 'Low', 1: 'Info'}
                        fig_sev = go.Figure()
                        for sev in [5, 4, 3, 2, 1]:
                            vals = [t['severity'].get(sev, 0) for t in trend_data]
                            if any(v > 0 for v in vals):
                                fig_sev.add_trace(go.Bar(
                                    x=dates, y=vals, name=sev_names[sev],
                                    marker_color=sev_colors_chart[sev]
                                ))
                        fig_sev.update_layout(
                            title='Severity Distribution Over Time', barmode='stack', height=300,
                            paper_bgcolor='#0e1117', plot_bgcolor='#1a1a2e',
                            font_color='#e0e0e0', xaxis_title='', yaxis_title='Stories',
                            margin=dict(l=40, r=20, t=40, b=30),
                            legend=dict(orientation='h', y=-0.2)
                        )
                        st.plotly_chart(fig_sev, use_container_width=True)
        
        st.markdown("---")
        
        # Apply filters
        filtered_stories = stories.copy()
        
        # Filter by severity if selected
        if 'selected_severity' in st.session_state:
            selected_sev = st.session_state['selected_severity']
            filtered_stories = [story for story in filtered_stories if story.get('severity') == selected_sev]
        
        # Display stories
        st.subheader(f"📰 Stories ({len(filtered_stories)} of {len(stories)})")
        
        if not filtered_stories:
            st.info(f"No stories found with current filters.")
            return
        
        # Group stories by category for better organization
        categories_with_stories = {}
        for story in filtered_stories:
            category = story.get('category', 'Uncategorized')
            if category not in categories_with_stories:
                categories_with_stories[category] = []
            categories_with_stories[category].append(story)
        
        # Display by category with collapsible sections
        for category, category_stories in categories_with_stories.items():
            emoji = '🟢'
            
            with st.expander(f"{emoji} {category} ({len(category_stories)})", expanded=True):
                for story in category_stories:
                    self.render_story_card(story)

if __name__ == "__main__":
    app = HistoryTechBriefApp()
    app.run()
