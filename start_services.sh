#!/bin/bash
# Startup script for n8n services
# This script starts Docker containers and the webhook server

cd /Users/jasvestis/n8n

echo "🚀 Starting n8n services..."

# Start Docker containers
echo "📦 Starting Docker containers..."
docker compose -f docker-compose-no-db.yml up -d

# Wait for containers to be ready
sleep 5

# Start webhook server if not already running
if ! lsof -i :8080 > /dev/null 2>&1; then
    echo "🌐 Starting webhook server on port 8080..."
    nohup python3 webhook_streamlit_server_history.py > /tmp/webhook_server.log 2>&1 &
    sleep 2
    
    if lsof -i :8080 > /dev/null 2>&1; then
        echo "✅ Webhook server started successfully"
    else
        echo "❌ Failed to start webhook server"
    fi
else
    echo "✅ Webhook server already running on port 8080"
fi

# Status check
echo ""
echo "📊 Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null
echo ""
echo "🌐 Webhook server: $(lsof -i :8080 > /dev/null 2>&1 && echo 'Running' || echo 'Not running')"
echo ""
echo "🔗 Access URLs:"
echo "   n8n:       http://localhost:5678"
echo "   Streamlit: http://localhost:8501"
echo "   Webhook:   http://localhost:8080/health"
