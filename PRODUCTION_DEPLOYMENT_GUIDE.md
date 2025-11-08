# 🚀 PRODUCTION DEPLOYMENT GUIDE - OVH with PM2

## Complete Guide to Deploy AI Screener to Production Server

---

## 📋 Prerequisites

**On Your OVH Server:**
- ✅ Ubuntu/Debian Linux (or CentOS)
- ✅ SSH access (root or sudo user)
- ✅ Domain name (optional, but recommended)
- ✅ Port 8501 open (for Streamlit)

**What We'll Install:**
- Python 3.8+
- PostgreSQL database
- Node.js & PM2 (to manage Python app)
- Nginx (reverse proxy)
- Git

---

## 🔧 STEP 1: Prepare Your Local Code for Git

### **1.1: Create .gitignore file**

Run this on your local machine:

```bash
cd "c:\python\MG AI\AI_Screener_Complete"
```

Create `.gitignore` file with this content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.sqlite3

# Environment variables
.env
*.env

# Logs
*.log
streamlit.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Data files
*.xlsx
*.csv
*.xls
data/
Nifty200_Complete_10yeardata.xlsx

# Models
models/*.pkl
models/*.joblib

# Temporary files
*.tmp
*.temp
```

### **1.2: Create production environment file template**

```bash
# Create .env.example (without sensitive data)
```

`.env.example`:
```
DHAN_CLIENT_ID=your_client_id_here
DHAN_ACCESS_TOKEN=your_access_token_here
DATABASE_URL=postgresql://username:password@localhost:5432/ai_screener
```

### **1.3: Initialize Git repository**

```bash
cd "c:\python\MG AI\AI_Screener_Complete"
git init
git add .
git commit -m "Initial commit - AI Screener v3.0"
```

### **1.4: Push to GitHub (or GitLab/Bitbucket)**

**Option A: GitHub**
```bash
# Create a new repository on github.com
# Then:
git remote add origin https://github.com/YOUR_USERNAME/ai-screener.git
git branch -M main
git push -u origin main
```

**Option B: GitLab**
```bash
git remote add origin https://gitlab.com/YOUR_USERNAME/ai-screener.git
git branch -M main
git push -u origin main
```

---

## 🖥️ STEP 2: Server Setup (OVH)

### **2.1: SSH into your OVH server**

```bash
ssh root@your-server-ip
# or
ssh username@your-server-ip
```

### **2.2: Update system**

```bash
sudo apt update
sudo apt upgrade -y
```

### **2.3: Install Python 3.11**

```bash
sudo apt install python3.11 python3.11-venv python3-pip -y

# Verify
python3.11 --version
```

### **2.4: Install PostgreSQL**

```bash
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE ai_screener;
CREATE USER screener_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_screener TO screener_user;
\q
EOF
```

### **2.5: Install Node.js and PM2**

```bash
# Install Node.js (LTS version)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Verify
node --version
npm --version

# Install PM2 globally
sudo npm install -g pm2

# Verify
pm2 --version
```

### **2.6: Install Nginx (reverse proxy)**

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 📦 STEP 3: Deploy Application

### **3.1: Create application directory**

```bash
sudo mkdir -p /var/www/ai-screener
sudo chown $USER:$USER /var/www/ai-screener
cd /var/www/ai-screener
```

### **3.2: Clone your repository**

```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/ai-screener.git .

# OR clone from GitLab
git clone https://gitlab.com/YOUR_USERNAME/ai-screener.git .
```

### **3.3: Create Python virtual environment**

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### **3.4: Install Python dependencies**

```bash
pip install --upgrade pip
pip install -r requirements_professional.txt

# Or if using requirements.txt
pip install streamlit pandas numpy scipy plotly python-dotenv psycopg2-binary dhanhq
```

### **3.5: Create production .env file**

```bash
nano .env
```

Add your production credentials:
```
DHAN_CLIENT_ID=1104147457
DHAN_ACCESS_TOKEN=your_production_token_here
DATABASE_URL=postgresql://screener_user:your_secure_password@localhost:5432/ai_screener
ENVIRONMENT=production
```

Save and exit (Ctrl+X, Y, Enter)

### **3.6: Setup database schema**

```bash
# Run database setup
source venv/bin/activate
python << EOF
from database.db_manager import get_db
db = get_db()
print("✅ Database initialized successfully!")
EOF
```

---

## 🚀 STEP 4: Configure PM2 to Manage Python/Streamlit

### **4.1: Create PM2 ecosystem file**

```bash
nano ecosystem.config.js
```

Add this configuration:

```javascript
module.exports = {
  apps: [{
    name: 'ai-screener-streamlit',
    script: '/var/www/ai-screener/venv/bin/streamlit',
    args: 'run enhanced_screener.py --server.port 8501 --server.address 0.0.0.0 --server.headless true',
    cwd: '/var/www/ai-screener',
    interpreter: 'none',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: '1'
    },
    error_file: '/var/www/ai-screener/logs/error.log',
    out_file: '/var/www/ai-screener/logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

Save and exit.

### **4.2: Create logs directory**

```bash
mkdir -p /var/www/ai-screener/logs
```

### **4.3: Start application with PM2**

```bash
cd /var/www/ai-screener
pm2 start ecosystem.config.js
```

### **4.4: Configure PM2 to start on boot**

```bash
pm2 startup
# Run the command it outputs (it will give you a sudo command)

pm2 save
```

### **4.5: Check PM2 status**

```bash
pm2 status
pm2 logs ai-screener-streamlit
```

---

## 🌐 STEP 5: Configure Nginx Reverse Proxy

### **5.1: Create Nginx configuration**

```bash
sudo nano /etc/nginx/sites-available/ai-screener
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain
    
    # Or use IP if no domain:
    # server_name your-server-ip;

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
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket support for Streamlit
        proxy_read_timeout 86400;
        proxy_redirect off;
    }

    # Health check endpoint
    location /healthz {
        proxy_pass http://localhost:8501/healthz;
        access_log off;
    }
}
```

Save and exit.

### **5.2: Enable the site**

```bash
sudo ln -s /etc/nginx/sites-available/ai-screener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **5.3: Configure firewall**

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 🔒 STEP 6: Setup SSL (HTTPS) - Optional but Recommended

### **6.1: Install Certbot**

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### **6.2: Get SSL certificate**

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts. Certbot will:
- Obtain SSL certificate
- Configure Nginx automatically
- Setup auto-renewal

### **6.3: Test auto-renewal**

```bash
sudo certbot renew --dry-run
```

---

## 📊 STEP 7: Verify Deployment

### **7.1: Check services**

```bash
# Check PM2
pm2 status

# Check Nginx
sudo systemctl status nginx

# Check PostgreSQL
sudo systemctl status postgresql

# View logs
pm2 logs ai-screener-streamlit --lines 50
```

### **7.2: Access your application**

**With domain:**
- HTTP: http://your-domain.com
- HTTPS: https://your-domain.com

**Without domain (IP only):**
- HTTP: http://your-server-ip

---

## 🔄 STEP 8: Future Updates (Deployment Workflow)

### **8.1: Update code on your local machine**

```bash
cd "c:\python\MG AI\AI_Screener_Complete"
git add .
git commit -m "Updated feature X"
git push origin main
```

### **8.2: Deploy to server**

Create a deployment script on the server:

```bash
nano /var/www/ai-screener/deploy.sh
```

Add:
```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Navigate to app directory
cd /var/www/ai-screener

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_professional.txt --upgrade

# Restart application
echo "🔄 Restarting application..."
pm2 restart ai-screener-streamlit

echo "✅ Deployment complete!"

# Show status
pm2 status
```

Make it executable:
```bash
chmod +x /var/www/ai-screener/deploy.sh
```

### **8.3: Deploy updates**

```bash
ssh username@your-server-ip
cd /var/www/ai-screener
./deploy.sh
```

---

## 📋 PM2 Useful Commands

```bash
# Start application
pm2 start ecosystem.config.js

# Stop application
pm2 stop ai-screener-streamlit

# Restart application
pm2 restart ai-screener-streamlit

# View logs (live)
pm2 logs ai-screener-streamlit

# View logs (last 100 lines)
pm2 logs ai-screener-streamlit --lines 100

# Monitor resources
pm2 monit

# List all processes
pm2 list

# Delete process
pm2 delete ai-screener-streamlit

# Save current PM2 processes
pm2 save

# View detailed info
pm2 show ai-screener-streamlit
```

---

## 🔍 Troubleshooting

### **Problem: Application won't start**

```bash
# Check logs
pm2 logs ai-screener-streamlit --lines 50

# Check if port is in use
sudo netstat -tulpn | grep 8501

# Test Streamlit directly
cd /var/www/ai-screener
source venv/bin/activate
streamlit run enhanced_screener.py
```

### **Problem: Database connection error**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test database connection
psql -U screener_user -d ai_screener -h localhost

# Check .env file
cat .env
```

### **Problem: 502 Bad Gateway**

```bash
# Check if Streamlit is running
pm2 status

# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### **Problem: Can't access from outside**

```bash
# Check firewall
sudo ufw status

# Open port 80
sudo ufw allow 80/tcp

# Open port 443 (HTTPS)
sudo ufw allow 443/tcp
```

---

## 🎯 Production Checklist

Before going live, ensure:

- [x] Code pushed to Git repository
- [x] Server has Python 3.11+ installed
- [x] PostgreSQL database created and configured
- [x] PM2 installed and configured
- [x] Nginx installed and configured
- [x] .env file with production credentials
- [x] SSL certificate installed (if using HTTPS)
- [x] Firewall configured properly
- [x] PM2 set to start on boot
- [x] Application accessible from internet
- [x] All services running (pm2 status)
- [x] Logs being written correctly
- [x] Database connections working
- [x] Dhan API credentials working

---

## 📈 Performance Optimization

### **Enable Gzip compression in Nginx**

Edit `/etc/nginx/nginx.conf`:

```nginx
http {
    # ... existing config ...
    
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
}
```

Reload Nginx:
```bash
sudo systemctl reload nginx
```

### **Optimize PostgreSQL**

Edit `/etc/postgresql/*/main/postgresql.conf`:

```conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 6MB
min_wal_size = 1GB
max_wal_size = 4GB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## 🔐 Security Best Practices

1. **Never commit .env file to Git**
   - Always use .env.example as template
   - Add .env to .gitignore

2. **Use strong database passwords**
   ```bash
   # Generate strong password
   openssl rand -base64 32
   ```

3. **Keep system updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Enable fail2ban**
   ```bash
   sudo apt install fail2ban -y
   sudo systemctl enable fail2ban
   ```

5. **Disable root SSH login**
   Edit `/etc/ssh/sshd_config`:
   ```
   PermitRootLogin no
   ```

6. **Use SSH keys instead of passwords**

---

## 📞 Quick Reference

**Application URL:** http://your-domain.com (or https:// if SSL enabled)

**Server locations:**
- App directory: `/var/www/ai-screener`
- Nginx config: `/etc/nginx/sites-available/ai-screener`
- Logs: `/var/www/ai-screener/logs/`
- Database: PostgreSQL on localhost:5432

**Commands:**
```bash
# Deploy updates
cd /var/www/ai-screener && ./deploy.sh

# View logs
pm2 logs ai-screener-streamlit

# Restart app
pm2 restart ai-screener-streamlit

# Check status
pm2 status
```

---

## 🎉 Success!

Your AI Screener is now running in production!

**Access it at:** http://your-domain.com (or your server IP)

**What's running:**
✅ Python/Streamlit application (managed by PM2)
✅ PostgreSQL database
✅ Nginx reverse proxy
✅ PM2 process manager
✅ Auto-restart on crash
✅ Auto-start on server reboot

---

**Need help?** Check the logs:
```bash
pm2 logs ai-screener-streamlit --lines 100
```

**Happy Trading! 📈💰🚀**

