#!/bin/bash
#############################################################
# AI SCREENER - FULLY AUTOMATED SERVER DEPLOYMENT
# Just run this script on your OVH server and answer prompts
#############################################################

set -e

clear
echo "=========================================================="
echo "  🚀 AI SCREENER - AUTOMATED DEPLOYMENT"
echo "=========================================================="
echo ""
echo "This script will automatically:"
echo "  ✅ Install all dependencies"
echo "  ✅ Setup PostgreSQL database"
echo "  ✅ Deploy your application"
echo "  ✅ Configure PM2 and Nginx"
echo "  ✅ Start everything"
echo ""
echo "Estimated time: 10-15 minutes"
echo ""
read -p "Press Enter to start..."

#############################################################
# COLLECT INFORMATION FIRST
#############################################################

echo ""
echo "=========================================================="
echo "  📋 STEP 1: Gather Information"
echo "=========================================================="
echo ""

read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your repository name (e.g., ai-screener): " REPO_NAME
read -p "Enter your Dhan Client ID: " DHAN_CLIENT_ID
read -p "Enter your Dhan Access Token: " DHAN_ACCESS_TOKEN
read -p "Enter your domain name (or press Enter to use IP): " DOMAIN_NAME

# Generate secure database password
DB_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-20)

echo ""
echo "✅ Information collected!"
echo ""

#############################################################
# SYSTEM UPDATE
#############################################################

echo "=========================================================="
echo "  📦 STEP 2: Updating System"
echo "=========================================================="
echo ""
sudo apt update
sudo apt upgrade -y
echo "✅ System updated"

#############################################################
# INSTALL PYTHON
#############################################################

echo ""
echo "=========================================================="
echo "  🐍 STEP 3: Installing Python 3.11"
echo "=========================================================="
echo ""
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y
echo "✅ Python 3.11 installed"
python3.11 --version

#############################################################
# INSTALL POSTGRESQL
#############################################################

echo ""
echo "=========================================================="
echo "  🗄️  STEP 4: Installing PostgreSQL"
echo "=========================================================="
echo ""
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
echo "✅ PostgreSQL installed"

# Create database and user
echo "Creating database..."
sudo -u postgres psql << EOF
CREATE DATABASE ai_screener;
CREATE USER screener_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE ai_screener TO screener_user;
ALTER DATABASE ai_screener OWNER TO screener_user;
\q
EOF
echo "✅ Database created"

#############################################################
# INSTALL NODE.JS & PM2
#############################################################

echo ""
echo "=========================================================="
echo "  📦 STEP 5: Installing Node.js & PM2"
echo "=========================================================="
echo ""
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2
echo "✅ Node.js and PM2 installed"
node --version
npm --version
pm2 --version

#############################################################
# INSTALL NGINX
#############################################################

echo ""
echo "=========================================================="
echo "  🌐 STEP 6: Installing Nginx"
echo "=========================================================="
echo ""
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
echo "✅ Nginx installed"

#############################################################
# DEPLOY APPLICATION
#############################################################

echo ""
echo "=========================================================="
echo "  📥 STEP 7: Deploying Application"
echo "=========================================================="
echo ""

# Create directory
sudo mkdir -p /var/www/ai-screener
sudo chown $USER:$USER /var/www/ai-screener
cd /var/www/ai-screener

# Clone repository
echo "Cloning repository..."
git clone https://github.com/${GITHUB_USER}/${REPO_NAME}.git .

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install streamlit pandas numpy scipy plotly python-dotenv psycopg2-binary dhanhq sqlalchemy

# Create .env file
echo "Creating configuration..."
cat > .env << EOF
DHAN_CLIENT_ID=${DHAN_CLIENT_ID}
DHAN_ACCESS_TOKEN=${DHAN_ACCESS_TOKEN}
DATABASE_URL=postgresql://screener_user:${DB_PASSWORD}@localhost:5432/ai_screener
ENVIRONMENT=production
SERVER_PORT=8501
SERVER_ADDRESS=0.0.0.0
EOF

# Create logs directory
mkdir -p logs

# Initialize database
echo "Initializing database..."
python << PYEOF
try:
    from database.db_manager import get_db
    db = get_db()
    print("✅ Database initialized successfully!")
except Exception as e:
    print(f"Database initialization: {e}")
    print("Will retry on first run...")
PYEOF

echo "✅ Application deployed"

#############################################################
# CONFIGURE PM2
#############################################################

echo ""
echo "=========================================================="
echo "  🚀 STEP 8: Configuring PM2"
echo "=========================================================="
echo ""

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOFPM2'
module.exports = {
  apps: [{
    name: 'ai-screener',
    script: '/var/www/ai-screener/venv/bin/streamlit',
    args: 'run enhanced_screener.py --server.port 8501 --server.address 0.0.0.0 --server.headless true',
    cwd: '/var/www/ai-screener',
    interpreter: 'none',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/error.log',
    out_file: './logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
EOFPM2

# Start with PM2
pm2 start ecosystem.config.js
pm2 save

# Setup PM2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp /home/$USER
pm2 save

echo "✅ PM2 configured"

#############################################################
# CONFIGURE NGINX
#############################################################

echo ""
echo "=========================================================="
echo "  🌐 STEP 9: Configuring Nginx"
echo "=========================================================="
echo ""

if [ -z "$DOMAIN_NAME" ]; then
    SERVER_NAME="_"
    PUBLIC_URL="http://$(curl -s ifconfig.me)"
else
    SERVER_NAME="$DOMAIN_NAME www.$DOMAIN_NAME"
    PUBLIC_URL="http://$DOMAIN_NAME"
fi

sudo tee /etc/nginx/sites-available/ai-screener > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name SERVER_NAME_PLACEHOLDER;
    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }
}
EOFNGINX

sudo sed -i "s/SERVER_NAME_PLACEHOLDER/$SERVER_NAME/g" /etc/nginx/sites-available/ai-screener

# Enable site
sudo ln -sf /etc/nginx/sites-available/ai-screener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Nginx configured"

#############################################################
# CONFIGURE FIREWALL
#############################################################

echo ""
echo "=========================================================="
echo "  🔒 STEP 10: Configuring Firewall"
echo "=========================================================="
echo ""

sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

echo "✅ Firewall configured"

#############################################################
# CREATE DEPLOY SCRIPT
#############################################################

echo ""
echo "Creating deployment script for future updates..."

cat > /var/www/ai-screener/deploy.sh << 'EOFDEPLOY'
#!/bin/bash
set -e
echo "🚀 Deploying updates..."
cd /var/www/ai-screener
git pull origin main
source venv/bin/activate
pip install -r requirements_professional.txt --upgrade --quiet 2>/dev/null || pip install streamlit pandas numpy scipy plotly python-dotenv psycopg2-binary dhanhq sqlalchemy --upgrade --quiet
pm2 restart ai-screener
echo "✅ Deployment complete!"
pm2 status
EOFDEPLOY

chmod +x /var/www/ai-screener/deploy.sh

#############################################################
# SAVE CREDENTIALS
#############################################################

echo ""
echo "Saving credentials to safe location..."
cat > /home/$USER/ai-screener-credentials.txt << EOF
AI SCREENER - CREDENTIALS
=========================

Database Password: ${DB_PASSWORD}
Dhan Client ID: ${DHAN_CLIENT_ID}
Dhan Access Token: ${DHAN_ACCESS_TOKEN}

Application URL: ${PUBLIC_URL}
Application Directory: /var/www/ai-screener

Commands:
---------
View status: pm2 status
View logs: pm2 logs ai-screener
Restart app: pm2 restart ai-screener
Deploy updates: cd /var/www/ai-screener && ./deploy.sh

KEEP THIS FILE SECURE!
EOF

chmod 600 /home/$USER/ai-screener-credentials.txt

#############################################################
# COMPLETION
#############################################################

echo ""
echo "=========================================================="
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "=========================================================="
echo ""
echo "🎉 Your AI Screener is now LIVE!"
echo ""
echo "📍 Access your application at:"
echo "   ${PUBLIC_URL}"
echo ""
echo "📊 Check status:"
echo "   pm2 status"
echo ""
echo "📋 View logs:"
echo "   pm2 logs ai-screener"
echo ""
echo "🔄 Deploy updates:"
echo "   cd /var/www/ai-screener && ./deploy.sh"
echo ""
echo "🔐 Your credentials are saved in:"
echo "   /home/$USER/ai-screener-credentials.txt"
echo ""
echo "=========================================================="
echo ""

# Show current status
pm2 status

echo ""
echo "Showing last 20 log lines..."
pm2 logs ai-screener --lines 20 --nostream

echo ""
echo "=========================================================="
echo "🎉 HAPPY TRADING! 📈💰"
echo "=========================================================="

