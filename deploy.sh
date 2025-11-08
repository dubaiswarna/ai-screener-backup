#!/bin/bash
# Deployment script for AI Screener
# Run this on your server after pushing code to Git

set -e

echo "=================================================="
echo "🚀 AI SCREENER - DEPLOYMENT SCRIPT"
echo "=================================================="
echo ""

# Navigate to app directory
cd /var/www/ai-screener

# Pull latest code
echo "📥 Step 1/5: Pulling latest code from Git..."
git pull origin main
echo "✅ Code updated"
echo ""

# Activate virtual environment
echo "🐍 Step 2/5: Activating Python virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install/update dependencies
echo "📦 Step 3/5: Installing/updating Python dependencies..."
pip install -r requirements_professional.txt --upgrade --quiet
echo "✅ Dependencies installed"
echo ""

# Run database migrations (if any)
echo "🗄️  Step 4/5: Checking database..."
python -c "from database.db_manager import get_db; db = get_db(); print('✅ Database connection verified')"
echo ""

# Restart application with PM2
echo "🔄 Step 5/5: Restarting application..."
pm2 restart ai-screener-streamlit
echo "✅ Application restarted"
echo ""

# Show current status
echo "=================================================="
echo "📊 CURRENT STATUS:"
echo "=================================================="
pm2 status
echo ""

# Show recent logs
echo "=================================================="
echo "📋 RECENT LOGS (last 20 lines):"
echo "=================================================="
pm2 logs ai-screener-streamlit --lines 20 --nostream
echo ""

echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "🌐 Your application should be running at:"
echo "   http://your-domain.com (or your server IP)"
echo ""
echo "📊 Monitor with: pm2 monit"
echo "📋 View logs with: pm2 logs ai-screener-streamlit"
echo ""

