#!/bin/bash

echo "=== ARES COMPLETE SYSTEM STARTUP ==="
echo "Starting UI Dashboards and Grafana Monitoring..."
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Starting Docker..."
    open -a Docker
    sleep 10
fi

# Start Grafana and InfluxDB
echo "1. Starting Grafana and InfluxDB..."
docker-compose up -d

# Wait for services to start
echo "2. Waiting for services to initialize..."
sleep 15

# Check if services are running
echo "3. Checking service status..."
docker-compose ps

# Start UI Dashboards
echo "4. Starting ARES UI Dashboards..."

# Start Complete Repository Dashboard
echo "   Starting Complete Repository Dashboard (Port 8503)..."
streamlit run complete_repo_dashboard.py --server.port 8503 --server.headless true &
DASHBOARD_PID_1=$!

# Start Executive Dashboard
echo "   Starting Executive Dashboard (Port 8501)..."
streamlit run Dashboard/executive_dashboard.py --server.port 8501 --server.headless true &
DASHBOARD_PID_2=$!

# Start Standalone Dashboard
echo "   Starting Standalone Dashboard (Port 8502)..."
streamlit run standalone_dashboard.py --server.port 8502 --server.headless true &
DASHBOARD_PID_3=$!

# Wait for UIs to start
sleep 5

echo
echo "=== SERVICES STARTED SUCCESSFULLY ==="
echo
echo "UI DASHBOARDS:"
echo "  Complete Repository: http://localhost:8503"
echo "  Executive Dashboard:  http://localhost:8501"
echo "  Standalone Dashboard: http://localhost:8502"
echo
echo "GRAFANA MONITORING:"
echo "  Grafana URL:          http://localhost:3000"
echo "  Username:             admin"
echo "  Password:             admin123"
echo
echo "INFLUXDB:"
echo "  InfluxDB URL:         http://localhost:8086"
echo "  Username:             admin"
echo "  Password:             password123"
echo "  Organization:         ares_corp"
echo "  Bucket:               qa_metrics"
echo
echo "=== RUNNING AI DEMO ==="
python3 demo_healing.py

echo
echo "=== MONITORING COMMANDS ==="
echo "View Grafana logs:"
echo "  docker-compose logs -f grafana"
echo
echo "View InfluxDB logs:"
echo "  docker-compose logs -f influxdb"
echo
echo "Stop all services:"
echo "  docker-compose down"
echo "  kill $DASHBOARD_PID_1 $DASHBOARD_PID_2 $DASHBOARD_PID_3"
echo
echo "=== ARES SYSTEM FULLY OPERATIONAL ==="

# Keep script running to show logs
echo "Press Ctrl+C to stop monitoring..."
echo
echo "Live Grafana Logs:"
docker-compose logs -f grafana &
GRAFANA_LOG_PID=$!

# Trap to cleanup on exit
trap "echo 'Stopping services...'; docker-compose down; kill $DASHBOARD_PID_1 $DASHBOARD_PID_2 $DASHBOARD_PID_3 $GRAFANA_LOG_PID 2>/dev/null; exit" INT

wait
