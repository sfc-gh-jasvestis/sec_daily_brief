#!/usr/bin/env python3
"""
Enhanced Streamlit app with 7-day history support for Daily Tech & Security Brief.
Shows current brief and allows browsing through the last 7 days of briefs.
"""

import streamlit as st
import json
import os
import requests
from datetime import datetime, timedelta
import pytz
from typing import Dict, List
import glob

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
    
    def render_story_card(self, story: Dict):
        """Render a story card"""
        companies = story.get('companies', [])
        if isinstance(companies, str):
            companies = companies.split(',') if companies else []
        
        # Format published date
        pub_date = story.get('published_date', '')
        formatted_date = self.format_singapore_time(pub_date) if pub_date else 'Date not available'
        
        st.markdown(f"""
        <div class="story-card">
            <div class="story-headline">
                <a href="{story.get('url', '#')}" target="_blank" style="text-decoration: none; color: #90caf9;">
                    {story.get('headline', 'No headline available')}
                </a>
            </div>
            <div style="color: #b0b0b0; font-size: 0.9rem; margin-bottom: 0.8rem;">
                📅 {formatted_date}
            </div>
            <div class="story-summary">
                {story.get('summary', 'No summary available')}
            </div>
            <div class="why-matters">
                <strong>💡 Why it matters:</strong> {story.get('why_matters', 'Analysis not available')}
            </div>
            <div>
                {' '.join([f'<span class="company-tag">{company.strip()}</span>' for company in companies[:8]])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_date_selector(self) -> str:
        """Render date selector and return selected date"""
        available_dates = self.get_available_dates()
        
        if not available_dates:
            st.warning("No historical data available yet. Run your workflow to generate data.")
            return None
        
        # Create date options
        date_options = ["Today (Latest)"] + [
            f"{date} ({self.format_date_display(date)})" 
            for date in available_dates
        ]
        
        selected_option = st.selectbox(
            "📅 Select Date",
            date_options,
            help="Choose which day's brief to view"
        )
        
        if selected_option == "Today (Latest)":
            return None  # Current data
        else:
            # Extract date from option string
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
            if selected_date:
                st.error(f"No data found for {selected_date}")
            else:
                st.warning("No current data available. Run your n8n workflow to generate data.")
            return
        
        # Show historical indicator if viewing past data
        if selected_date:
            singapore_date = data.get('singapore_date', selected_date)
            st.markdown(f"""
            <div class="historical-indicator">
                📚 Viewing Historical Brief: {singapore_date}
            </div>
            """, unsafe_allow_html=True)
        
        # Brief metadata
        metadata = data.get('metadata', {})
        
        # Summary metrics with responsive layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Stories", data.get('total_stories', 0))
        
        with col2:
            st.metric("Categories", len(data.get('categories', [])))
        
        # Generated time and source in full-width sections for better readability
        st.markdown("---")
        
        # Generated time section
        last_update = metadata.get('last_update', data.get('generated_at', ''))
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
        
        # Check if we have stories
        stories = data.get('stories', [])
        if not stories:
            st.warning("No stories available in this brief.")
            return
        
        # Group categories by threat level for better navigation
        category_groups = {
            '🚨 Critical Threats': ['Zero-Day Exploits', 'Threat Intelligence & APTs', 'Breaches/Ransomware'],
            '🛡️ Vulnerabilities & Defense': ['Vulnerabilities', 'Incident Response & Forensics', 'Identity & Access Management'],
            '🏢 Enterprise & Infrastructure': ['Supply Chain Security', 'Cloud/SaaS', 'Critical Infrastructure & OT/ICS', 'Mobile & IoT Security'],
            '📋 Governance & Business': ['Policy/Regulation', 'Data Privacy & Protection', 'Compliance & Audit'],
            '💡 Innovation & Insights': ['Security Operations & Tools', 'Startups/Funding', 'Research', 'AI/ML']
        }
        
        # Category filter with enhanced UI
        st.markdown("---")
        st.markdown("### 🔍 Filter & Navigate")
        
        # Create tabs for filter options
        filter_tab, group_tab = st.tabs(["📁 By Category", "🎯 By Threat Level"])
        
        with filter_tab:
            all_categories = data.get('categories', [])
            
            # Count stories per category
            category_counts = {}
            for story in stories:
                cat = story.get('category', 'Uncategorized')
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Create category options with counts (only show categories with stories)
            categories_with_stories = [cat for cat in all_categories if category_counts.get(cat, 0) > 0]
            category_options = ['All Categories'] + [
                f"{cat} ({category_counts.get(cat, 0)})" 
                for cat in categories_with_stories
            ]
            
            selected_option = st.selectbox(
                "Select a category to filter",
                category_options,
                key=f"category_{selected_date or 'current'}"
            )
            
            # Extract actual category name - handle the count in parentheses
            if selected_option == 'All Categories':
                selected_category = 'All'
            else:
                # Split on ' (' and take the first part to remove the count
                selected_category = selected_option.rsplit(' (', 1)[0]
        
        with group_tab:
            # Quick jump links to category groups
            st.markdown("**Jump to section:**")
            
            cols = st.columns(2)
            for idx, (group_name, group_cats) in enumerate(category_groups.items()):
                # Count stories in this group
                group_count = sum(category_counts.get(cat, 0) for cat in group_cats)
                
                with cols[idx % 2]:
                    if st.button(f"{group_name} ({group_count})", use_container_width=True, key=f"group_{idx}"):
                        st.session_state['selected_group'] = group_name
            
            # Show selected group filter
            if 'selected_group' in st.session_state:
                st.success(f"Showing: {st.session_state['selected_group']}")
                if st.button("Clear Filter", use_container_width=True):
                    del st.session_state['selected_group']
        
        st.markdown("---")
        
        # Apply filters
        filtered_stories = stories.copy()
        
        # Filter by category if selected
        if selected_category != 'All':
            filtered_stories = [story for story in filtered_stories if story.get('category') == selected_category]
        
        # Filter by group if selected
        if 'selected_group' in st.session_state:
            selected_group = st.session_state['selected_group']
            if selected_group in category_groups:
                group_categories = category_groups[selected_group]
                filtered_stories = [story for story in filtered_stories if story.get('category') in group_categories]
        
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
            # Determine emoji based on category group
            emoji = '🔴'
            for group_name, group_cats in category_groups.items():
                if category in group_cats:
                    if 'Critical' in group_name:
                        emoji = '🚨'
                    elif 'Vulnerabilities' in group_name:
                        emoji = '🛡️'
                    elif 'Enterprise' in group_name:
                        emoji = '🏢'
                    elif 'Governance' in group_name:
                        emoji = '📋'
                    elif 'Innovation' in group_name:
                        emoji = '💡'
                    break
            
            with st.expander(f"{emoji} {category} ({len(category_stories)})", expanded=True):
                for story in category_stories:
                    self.render_story_card(story)

if __name__ == "__main__":
    app = HistoryTechBriefApp()
    app.run()
