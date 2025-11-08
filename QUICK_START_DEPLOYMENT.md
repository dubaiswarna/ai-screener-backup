# ⚡ QUICK START - Deploy to OVH in 15 Minutes

This is the fastest way to get your AI Screener live on your OVH server.

---

## 🎯 Overview

**Time:** 15-20 minutes  
**Difficulty:** Beginner-friendly  
**What you need:**
- OVH server with SSH access
- Domain name (optional)
- Your Dhan API credentials

---

## 📦 Step 1: Prepare Your Code (2 minutes)

### On your Windows PC:

```powershell
# 1. Open PowerShell in your project directory
cd "c:\python\MG AI\AI_Screener_Complete"

# 2. Initialize Git (if not done already)
git init
git add .
git commit -m "Initial commit - Production ready"

# 3. Push to GitHub
# First create a new repository on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-screener.git
git branch -M main
git push -u origin main
```

✅ **Done!** Your code is now on GitHub.

---

## 🖥️ Step 2: Server Setup (10 minutes)

### Connect to your OVH server:

```bash
ssh root@your-server-ip
```

### Run this ONE command to install everything:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ai-screener/main/install.sh | bash
```

**OR** Copy-paste this complete setup script:

```bash
#!/bin/bash
set -e

echo "🚀 AI Screener - Automated Setup"
echo "================================"

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python..."
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL
echo "🗄️  Installing PostgreSQL..."
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Node.js & PM2
echo "📦 Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/ai-screener
sudo chown $USER:$USER /var/www/ai-screener
cd /var/www/ai-screener

# Clone repository
echo "📥 Cloning repository..."
read -p "Enter your GitHub repository URL: " REPO_URL
git clone $REPO_URL .

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_professional.txt

# Setup database
echo "🗄️  Setting up database..."
read -p "Enter database password: " DB_PASSWORD
sudo -u postgres psql << EOF
CREATE DATABASE ai_screener;
CREATE USER screener_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE ai_screener TO screener_user;
\q
EOF

# Create .env file
echo "⚙️  Creating configuration file..."
read -p "Enter your Dhan Client ID: " DHAN_CLIENT_ID
read -p "Enter your Dhan Access Token: " DHAN_ACCESS_TOKEN

cat > .env << EOF
DHAN_CLIENT_ID=$DHAN_CLIENT_ID
DHAN_ACCESS_TOKEN=$DHAN_ACCESS_TOKEN
DATABASE_URL=postgresql://screener_user:$DB_PASSWORD@localhost:5432/ai_screener
ENVIRONMENT=production
EOF

# Initialize database
echo "🔧 Initializing database..."
python << EOF
from database.db_manager import get_db
db = get_db()
print("✅ Database initialized")
EOF

# Create logs directory
mkdir -p logs

# Start with PM2
echo "🚀 Starting application..."
pm2 start ecosystem.config.js
pm2 startup
pm2 save

# Configure Nginx
echo "🌐 Configuring Nginx..."
read -p "Enter your domain (or press Enter for IP-only access): " DOMAIN

if [ -z "$DOMAIN" ]; then
    SERVER_NAME="_"
else
    SERVER_NAME="$DOMAIN www.$DOMAIN"
fi

sudo tee /etc/nginx/sites-available/ai-screener > /dev/null << EOF
server {
    listen 80;
    server_name $SERVER_NAME;
    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ai-screener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# Make deploy script executable
chmod +x deploy.sh

echo ""
echo "=================================================="
echo "✅ SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "🌐 Your application is now running!"
echo ""
if [ -z "$DOMAIN" ]; then
    echo "📍 Access at: http://$(curl -s ifconfig.me)"
else
    echo "📍 Access at: http://$DOMAIN"
fi
echo ""
echo "📊 Check status: pm2 status"
echo "📋 View logs: pm2 logs ai-screener-streamlit"
echo "🔄 Deploy updates: ./deploy.sh"
echo ""
echo "🎉 Happy Trading!"
echo "=================================================="
```

Save this as `quick-install.sh` and run:

```bash
chmod +x quick-install.sh
./quick-install.sh
```

---

## ✅ Step 3: Verify (2 minutes)

### Check if everything is running:

```bash
# Check PM2
pm2 status

# Check Nginx
sudo systemctl status nginx

# View logs
pm2 logs ai-screener-streamlit --lines 20
```

### Access your application:

Open browser and go to:
- **With domain:** http://your-domain.com
- **Without domain:** http://your-server-ip

---

## 🎉 You're Live!

Your AI Screener is now running in production!

### What's next?

1. **Test the application:**
   - Go to S&R Analysis
   - Try batch analysis with multiple stocks
   - Check if all features work

2. **Setup SSL (optional):**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

3. **Deploy updates:**
   ```bash
   cd /var/www/ai-screener
   ./deploy.sh
   ```

---

## 📞 Quick Commands

```bash
# View status
pm2 status

# Restart app
pm2 restart ai-screener-streamlit

# View logs
pm2 logs ai-screener-streamlit

# Deploy updates
cd /var/www/ai-screener && ./deploy.sh

# Stop app
pm2 stop ai-screener-streamlit
```

---

## 🐛 Troubleshooting

**Problem: Can't access the site**
```bash
# Check if Streamlit is running
pm2 status

# Check firewall
sudo ufw status

# Check Nginx
sudo systemctl status nginx
```

**Problem: Application crashes**
```bash
# View error logs
pm2 logs ai-screener-streamlit --lines 100

# Restart
pm2 restart ai-screener-streamlit
```

**Problem: Database connection error**
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
psql -U screener_user -d ai_screener -h localhost
```

---

## 📚 Full Documentation

For detailed information, see:
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Complete guide
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist

---

**That's it! You're done in 15 minutes! 🚀📈💰**

