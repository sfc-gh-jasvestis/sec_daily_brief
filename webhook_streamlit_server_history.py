#!/usr/bin/env python3
"""
Enhanced webhook server with 7-day history support for n8n workflow data.
Saves daily files and maintains a 7-day rolling history.
"""

import json
import os
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from pathlib import Path
import glob

app = Flask(__name__)

# Configuration
HISTORY_DIR = "history"
CURRENT_FILE = "tech_brief.json"
MAX_HISTORY_DAYS = 7

def ensure_history_dir():
    """Ensure the history directory exists"""
    Path(HISTORY_DIR).mkdir(exist_ok=True)

def cleanup_old_files():
    """Remove files older than MAX_HISTORY_DAYS"""
    cutoff_date = datetime.now() - timedelta(days=MAX_HISTORY_DAYS)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    pattern = os.path.join(HISTORY_DIR, "tech_brief_*.json")
    old_files = []
    
    for file_path in glob.glob(pattern):
        filename = os.path.basename(file_path)
        # Extract date from filename: tech_brief_2025-09-30.json
        try:
            date_str = filename.replace('tech_brief_', '').replace('.json', '')
            if date_str < cutoff_str:
                os.remove(file_path)
                old_files.append(filename)
                print(f"🗑️ Removed old file: {filename}")
        except Exception as e:
            print(f"⚠️ Error processing file {filename}: {e}")
    
    if old_files:
        print(f"🧹 Cleaned up {len(old_files)} old files")
    
    return old_files

def get_previously_seen_urls():
    """Get all story URLs from previous historical files (excluding today)"""
    ensure_history_dir()
    current_date = datetime.now().strftime('%Y-%m-%d')
    pattern = os.path.join(HISTORY_DIR, "tech_brief_*.json")
    seen_urls = set()
    
    for file_path in glob.glob(pattern):
        filename = os.path.basename(file_path)
        try:
            date_str = filename.replace('tech_brief_', '').replace('.json', '')
            
            # Skip today's file (we want to dedupe against previous days only)
            if date_str == current_date:
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stories = data.get('stories', [])
                for story in stories:
                    url = story.get('url', '').strip()
                    if url:
                        seen_urls.add(url)
        except Exception as e:
            print(f"⚠️ Error reading {filename} for deduplication: {e}")
    
    print(f"🔍 Found {len(seen_urls)} previously seen story URLs across {len(glob.glob(pattern)) - 1} historical files")
    return seen_urls

def deduplicate_stories(data):
    """Remove stories that appeared in previous days"""
    if 'stories' not in data or not isinstance(data['stories'], list):
        print("⚠️ No stories array found in data")
        return data
    
    original_count = len(data['stories'])
    previously_seen = get_previously_seen_urls()
    
    # Filter out stories we've seen before
    new_stories = []
    duplicate_count = 0
    
    for story in data['stories']:
        url = story.get('url', '').strip()
        if url in previously_seen:
            duplicate_count += 1
            print(f"🔄 Skipping duplicate: {story.get('headline', 'Unknown')[:60]}...")
        else:
            new_stories.append(story)
    
    # Update data with deduplicated stories
    data['stories'] = new_stories
    data['total_stories'] = len(new_stories)
    
    # Update categories count if needed
    if new_stories:
        unique_categories = sorted(set(story.get('category', 'Uncategorized') for story in new_stories))
        data['categories'] = unique_categories
    else:
        data['categories'] = []
    
    # Add deduplication metadata
    data['deduplication'] = {
        'original_count': original_count,
        'duplicate_count': duplicate_count,
        'new_stories_count': len(new_stories),
        'previously_seen_urls': len(previously_seen)
    }
    
    print(f"✂️ Deduplication: {original_count} stories → {len(new_stories)} new stories ({duplicate_count} duplicates removed)")
    
    return data

def save_historical_file(data):
    """Save data to both current file and historical file"""
    ensure_history_dir()
    
    # Get current date for filename
    current_date = datetime.now().strftime('%Y-%m-%d')
    historical_file = os.path.join(HISTORY_DIR, f"tech_brief_{current_date}.json")
    
    # Add metadata for historical tracking
    data['saved_at'] = datetime.now().isoformat()
    data['file_date'] = current_date
    
    try:
        # Save to current file (for main app)
        with open(CURRENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved current file: {CURRENT_FILE}")
        
        # Save to historical file
        with open(historical_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📁 Saved historical file: {historical_file}")
        
        # Cleanup old files
        cleanup_old_files()
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving files: {e}")
        return False

def get_available_dates():
    """Get list of available historical dates"""
    ensure_history_dir()
    pattern = os.path.join(HISTORY_DIR, "tech_brief_*.json")
    dates = []
    
    for file_path in glob.glob(pattern):
        filename = os.path.basename(file_path)
        try:
            date_str = filename.replace('tech_brief_', '').replace('.json', '')
            dates.append(date_str)
        except:
            continue
    
    # Sort dates in descending order (newest first)
    dates.sort(reverse=True)
    return dates

@app.route('/webhook/tech-brief', methods=['POST'])
def receive_tech_brief():
    """Receive tech brief data from n8n workflow (already deduplicated at workflow layer)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        print(f"📨 Received data with {data.get('total_stories', 0)} stories")
        print(f"🕒 Generated at: {data.get('generated_at', 'Unknown')}")
        print(f"ℹ️  Deduplication now handled at workflow layer (before AI processing)")
        
        # Save to both current and historical files
        success = save_historical_file(data)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Data saved successfully",
                "stories": data.get('total_stories', 0),
                "timestamp": datetime.now().isoformat(),
                "file_date": data.get('file_date', 'Unknown')
            })
        else:
            return jsonify({"error": "Failed to save data"}), 500
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get list of available historical dates"""
    try:
        dates = get_available_dates()
        return jsonify({
            "available_dates": dates,
            "total_days": len(dates),
            "max_history_days": MAX_HISTORY_DAYS
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<date>', methods=['GET'])
def get_historical_data(date):
    """Get data for a specific historical date"""
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
        
        historical_file = os.path.join(HISTORY_DIR, f"tech_brief_{date}.json")
        
        if not os.path.exists(historical_file):
            return jsonify({"error": f"No data found for date {date}"}), 404
        
        with open(historical_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "server": "n8n-streamlit-webhook-history",
        "timestamp": datetime.now().isoformat(),
        "history_enabled": True,
        "max_history_days": MAX_HISTORY_DAYS,
        "available_dates": len(get_available_dates())
    })

if __name__ == '__main__':
    print("🚀 Starting n8n Streamlit Webhook Server with History Support")
    print(f"📁 History directory: {HISTORY_DIR}")
    print(f"📅 Max history days: {MAX_HISTORY_DAYS}")
    print(f"🌐 Server will run on http://localhost:8080")
    print("📡 Webhook endpoint: http://localhost:8080/webhook/tech-brief")
    print("📊 History API: http://localhost:8080/api/history")
    print("🔍 Health check: http://localhost:8080/health")
    
    # Ensure history directory exists
    ensure_history_dir()
    
    # Initial cleanup
    cleanup_old_files()
    
    app.run(host='0.0.0.0', port=8080, debug=True)
