#!/bin/bash

echo "🎯 KodeKloud Records Store - Capstone Setup Verification"
echo "======================================================"
echo

# Check if docker-compose is running
echo "1. Checking Docker Compose services..."
if docker-compose ps | grep -q "Up"; then
    echo "   ✅ Docker Compose services are running"
else
    echo "   ❌ Docker Compose services not running. Please run: docker-compose up -d"
    exit 1
fi

# Check if API is responding
echo "2. Checking API health..."
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ API is responding at http://localhost:8000"
else
    echo "   ❌ API not responding. Check docker logs: docker-compose logs api"
fi

# Check Grafana access
echo "3. Checking Grafana access..."
if curl -f -s http://localhost:3000/api/health > /dev/null; then
    echo "   ✅ Grafana is accessible at http://localhost:3000"
    echo "   📊 Engineer Dashboard: http://localhost:3000/d/engineer-dashboard"
    echo "   📈 Executive Dashboard: http://localhost:3000/d/executive-dashboard"
else
    echo "   ❌ Grafana not accessible. Check: docker-compose logs grafana"
fi

# Check Prometheus
echo "4. Checking Prometheus..."
if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
    echo "   ✅ Prometheus is running at http://localhost:9090"
else
    echo "   ❌ Prometheus not accessible. Check: docker-compose logs prometheus"
fi

# Check if GitHub repo is forked
echo "5. Checking repository setup..."
if git remote -v | grep -q "origin.*github.com"; then
    ORIGIN_URL=$(git remote get-url origin)
    echo "   ✅ Repository forked: $ORIGIN_URL"
else
    echo "   ❌ Repository not properly forked from GitHub"
fi

# Check for webhook secret
echo "6. Checking webhook configuration..."
echo "   ℹ️  To verify webhook setup:"
echo "   - Go to your GitHub repository: Settings → Secrets and variables → Actions"
echo "   - Ensure SLACK_WEBHOOK_URL (or DISCORD_WEBHOOK_URL) is configured"
echo "   - Test with: Actions → Capstone Test Notification → Run workflow"

echo
echo "🎯 Capstone Prerequisites Summary:"
echo "=================================="
echo "✅ Prerequisites that should be ready:"
echo "   - Forked KodeKloud Records Store repository"
echo "   - Local environment running (Docker Compose)"
echo "   - Grafana dashboards accessible"
echo "   - Webhook notifications set up from Module 6"
echo
echo "📚 If any items are missing:"
echo "   - Review Module 6 configuration management lesson"
echo "   - Review Module 7 observability setup"
echo "   - Ensure docker-compose up -d completed successfully"
echo
echo "🚀 Ready for capstone? Visit: http://localhost:3000"
echo "   Default login: admin / admin" 