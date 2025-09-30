#!/usr/bin/env python3
"""
Startup script for the enhanced n8n workflow system with 7-day history support.
Starts both the webhook server and Streamlit app with history features.
"""

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Shutting down services...')
    sys.exit(0)

def check_port(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_services():
    """Start webhook server and Streamlit app"""
    print("🚀 Starting Enhanced n8n Workflow System with 7-Day History")
    print("=" * 60)
    
    # Check if ports are available
    if check_port(8080):
        print("⚠️  Port 8080 is already in use. Please stop the existing service.")
        return False
    
    if check_port(8501):
        print("⚠️  Port 8501 is already in use. Please stop the existing service.")
        return False
    
    # Create history directory
    Path("history").mkdir(exist_ok=True)
    print("📁 Created history directory")
    
    processes = []
    
    try:
        # Start webhook server with history support
        print("🌐 Starting webhook server with history support...")
        webhook_process = subprocess.Popen([
            sys.executable, "webhook_streamlit_server_history.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        processes.append(("Webhook Server", webhook_process))
        
        # Wait a moment for webhook server to start
        time.sleep(3)
        
        # Start Streamlit app with history support
        print("📊 Starting Streamlit app with history support...")
        streamlit_process = subprocess.Popen([
            "streamlit", "run", "streamlit_history_app.py", 
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--theme.base", "dark"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        processes.append(("Streamlit App", streamlit_process))
        
        # Wait a moment for services to start
        time.sleep(5)
        
        print("\n✅ Services started successfully!")
        print("=" * 60)
        print("🌐 Webhook Server: http://localhost:8080")
        print("📊 Streamlit App: http://localhost:8501")
        print("📡 Webhook Endpoint: http://localhost:8080/webhook/tech-brief")
        print("📅 History API: http://localhost:8080/api/history")
        print("🔍 Health Check: http://localhost:8080/health")
        print("=" * 60)
        print("\n🔧 Features Available:")
        print("• 📅 7-day rolling history of daily briefs")
        print("• 🇸🇬 Singapore timezone display")
        print("• 📊 Enhanced story categorization")
        print("• 🔄 Auto-refresh capabilities")
        print("• 📱 Responsive dark theme UI")
        print("\n💡 Usage:")
        print("1. Run your n8n workflow to generate daily briefs")
        print("2. View current brief at http://localhost:8501")
        print("3. Browse history using the sidebar date selector")
        print("4. Data is automatically saved and old files cleaned up")
        print("\n⌨️  Press Ctrl+C to stop all services")
        
        # Monitor processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} has stopped unexpectedly")
                    return False
    
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return False
    
    finally:
        # Clean up processes
        print("🧹 Cleaning up processes...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 Force killed {name}")
            except Exception as e:
                print(f"⚠️  Error stopping {name}: {e}")
    
    return True

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start services
    success = start_services()
    
    if success:
        print("👋 Services stopped successfully")
    else:
        print("❌ Services stopped with errors")
        sys.exit(1)
