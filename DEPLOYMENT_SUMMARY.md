# 🚀 DEPLOYMENT TO OVH - SUMMARY

## ✅ What I've Created For You

I've prepared **everything** you need to deploy your AI Screener to your OVH server with PM2:

### 📁 **Files Created:**

1. **`.gitignore`** - Excludes sensitive files from Git
2. **`.env.example`** - Template for environment variables
3. **`ecosystem.config.js`** - PM2 configuration (manages your Python app)
4. **`deploy.sh`** - One-command deployment script
5. **`nginx.conf`** - Nginx reverse proxy configuration
6. **`PRODUCTION_DEPLOYMENT_GUIDE.md`** - Complete step-by-step guide
7. **`DEPLOYMENT_CHECKLIST.md`** - Checkbox checklist
8. **`QUICK_START_DEPLOYMENT.md`** - 15-minute quick start

---

## 🎯 Your Next Steps

### **Step 1: Push Code to Git (5 minutes)**

```powershell
# On your Windows PC
cd "c:\python\MG AI\AI_Screener_Complete"

# Initialize Git
git init
git add .
git commit -m "Production ready - AI Screener v3.0"

# Create repository on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-screener.git
git branch -M main
git push -u origin main
```

### **Step 2: Setup OVH Server (10 minutes)**

```bash
# SSH into your OVH server
ssh root@your-server-ip

# Run these commands one by one:
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 4. Install Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

# 5. Install Nginx
sudo apt install nginx -y
```

### **Step 3: Deploy Application (5 minutes)**

```bash
# Create directory
sudo mkdir -p /var/www/ai-screener
sudo chown $USER:$USER /var/www/ai-screener
cd /var/www/ai-screener

# Clone your code
git clone https://github.com/YOUR_USERNAME/ai-screener.git .

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements_professional.txt

# Create .env file (copy from .env.example and fill in values)
cp .env.example .env
nano .env

# Start with PM2
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

### **Step 4: Configure Nginx (2 minutes)**

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/ai-screener

# Edit to add your domain
sudo nano /etc/nginx/sites-available/ai-screener
# Change: server_name your-domain.com;

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-screener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Open firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## ✅ Done! Your App is Live!

### **Access your application:**
- http://your-domain.com (or http://your-server-ip)

### **Manage your application:**

```bash
# Check status
pm2 status

# View logs
pm2 logs ai-screener-streamlit

# Restart
pm2 restart ai-screener-streamlit

# Deploy updates (after pushing to Git)
cd /var/www/ai-screener
./deploy.sh
```

---

## 🔧 Why PM2 for Python App?

**PM2 is perfect for managing your Python/Streamlit app because:**

✅ **Auto-restart** - If app crashes, PM2 restarts it immediately
✅ **Startup script** - App starts automatically on server reboot
✅ **Log management** - Centralized logs with rotation
✅ **Zero downtime** - Graceful restarts without downtime
✅ **Monitoring** - Built-in CPU/memory monitoring
✅ **Cluster mode** - Scale to multiple instances if needed

**Node.js is NOT required for your app** - PM2 just uses Node.js as the process manager, but runs your Python/Streamlit application.

---

## 📊 Architecture Overview

```
Internet
    ↓
Nginx (Port 80/443)
    ↓ (proxy to)
Streamlit App (Port 8501)
    ↓ (managed by)
PM2 Process Manager
    ↓ (connects to)
PostgreSQL Database (Port 5432)
```

---

## 📚 Documentation Guide

**For different needs, read:**

1. **Quick start (15 min):** `QUICK_START_DEPLOYMENT.md`
2. **Complete guide:** `PRODUCTION_DEPLOYMENT_GUIDE.md`
3. **Checklist:** `DEPLOYMENT_CHECKLIST.md`

---

## 🎯 Key Configuration Files

### **ecosystem.config.js** (PM2 Config)
```javascript
module.exports = {
  apps: [{
    name: 'ai-screener-streamlit',
    script: 'venv/bin/streamlit',
    args: 'run enhanced_screener.py --server.port 8501',
    // ... more config
  }]
};
```

### **.env** (Environment Variables)
```
DHAN_CLIENT_ID=1104147457
DHAN_ACCESS_TOKEN=your_token_here
DATABASE_URL=postgresql://user:pass@localhost/db
```

### **nginx.conf** (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://localhost:8501;
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🔄 Future Updates Workflow

### **On your local machine:**
```powershell
# Make changes to code
# Test locally
# Commit and push
git add .
git commit -m "Updated feature X"
git push origin main
```

### **On your server:**
```bash
# Deploy with one command
cd /var/www/ai-screener
./deploy.sh
```

**The deploy.sh script will:**
1. Pull latest code from Git
2. Install/update dependencies
3. Restart application with PM2
4. Show status and logs

---

## 🐛 Common Issues & Solutions

### **Issue: Port 8501 already in use**
```bash
# Find process using port
sudo netstat -tulpn | grep 8501
# Kill process
sudo kill -9 PID
# Restart PM2
pm2 restart ai-screener-streamlit
```

### **Issue: Database connection error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
# Check credentials in .env
cat .env
# Test connection
psql -U screener_user -d ai_screener -h localhost
```

### **Issue: 502 Bad Gateway**
```bash
# Check if app is running
pm2 status
# Check logs
pm2 logs ai-screener-streamlit --lines 100
# Restart
pm2 restart ai-screener-streamlit
```

---

## 📞 Quick Commands Reference Card

```bash
# PM2 Commands
pm2 list                                    # List all processes
pm2 status                                  # Show status
pm2 start ecosystem.config.js              # Start app
pm2 restart ai-screener-streamlit          # Restart
pm2 stop ai-screener-streamlit             # Stop
pm2 delete ai-screener-streamlit           # Remove
pm2 logs ai-screener-streamlit             # View logs
pm2 logs ai-screener-streamlit --lines 100 # Last 100 lines
pm2 monit                                  # Real-time monitor
pm2 save                                   # Save config
pm2 resurrect                              # Restore saved config

# System Commands
sudo systemctl restart nginx               # Restart Nginx
sudo systemctl status postgresql           # Check database
sudo ufw status                            # Check firewall
htop                                       # Monitor resources

# Git & Deployment
git pull origin main                       # Pull updates
./deploy.sh                                # Deploy
```

---

## ✅ Checklist Before Going Live

- [ ] Code tested locally
- [ ] All sensitive data in .env (not in code)
- [ ] Code pushed to Git repository
- [ ] Server has all dependencies installed
- [ ] Database created and accessible
- [ ] .env file created on server with credentials
- [ ] PM2 running and auto-starts on boot
- [ ] Nginx configured and running
- [ ] Firewall configured (ports 80, 443, 22 open)
- [ ] Application accessible from internet
- [ ] SSL certificate installed (optional but recommended)
- [ ] Tested all features (S&R single & batch)
- [ ] Logs are being written
- [ ] deploy.sh script tested

---

## 🎉 Success Criteria

### **You know it's working when:**

✅ `pm2 status` shows app as "online"
✅ Browser loads http://your-domain.com
✅ Dashboard displays correctly
✅ S&R Analysis (single) works
✅ Batch Analysis works
✅ No errors in `pm2 logs`
✅ Database queries work
✅ Can navigate all pages

---

## 💡 Pro Tips

1. **Always test locally first** before deploying
2. **Use deploy.sh** for consistent deployments
3. **Monitor logs** after each deployment
4. **Backup .env file** securely (it has your credentials)
5. **Setup SSL** for production (use Certbot - it's free)
6. **Use strong database passwords**
7. **Keep system updated** with `apt update && apt upgrade`
8. **Setup automated database backups**

---

## 📚 Additional Resources

- **PM2 Documentation:** https://pm2.keymetrics.io/
- **Streamlit Deployment:** https://docs.streamlit.io/knowledge-base/deploy
- **Nginx Configuration:** https://nginx.org/en/docs/
- **Certbot (SSL):** https://certbot.eff.org/

---

## 🆘 Need Help?

Check the detailed guides:
1. `PRODUCTION_DEPLOYMENT_GUIDE.md` - Complete guide with explanations
2. `QUICK_START_DEPLOYMENT.md` - Fast 15-minute setup
3. `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist

Or check logs:
```bash
pm2 logs ai-screener-streamlit --lines 200
```

---

## 🎯 Summary

**What you have:**
- Python/Streamlit AI Screener application
- Support & Resistance analysis (single & batch)
- PostgreSQL database for persistence

**What we're deploying to:**
- OVH VPS/Cloud server
- Managed by PM2 process manager
- Proxied through Nginx
- Accessible via domain/IP

**Time to deploy:** 20-30 minutes total

---

**Ready to deploy? Start with `QUICK_START_DEPLOYMENT.md`! 🚀**

**Happy Trading! 📈💰**

