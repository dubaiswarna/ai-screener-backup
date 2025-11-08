# 🚀 DEPLOYMENT CHECKLIST

Use this checklist to ensure smooth deployment to production.

---

## 📋 PRE-DEPLOYMENT (Local)

- [ ] **Test application locally**
  - [ ] All features working
  - [ ] No errors in logs
  - [ ] Database connections working
  - [ ] S&R analysis working (single & batch)

- [ ] **Prepare Git repository**
  - [ ] Create `.gitignore` file
  - [ ] Create `.env.example` file
  - [ ] Remove sensitive data from code
  - [ ] Test on fresh virtual environment

- [ ] **Commit and push code**
  ```bash
  cd "c:\python\MG AI\AI_Screener_Complete"
  git init
  git add .
  git commit -m "Production ready - v3.0"
  git remote add origin YOUR_REPO_URL
  git push -u origin main
  ```

---

## 🖥️ SERVER SETUP

- [ ] **Connect to OVH server**
  ```bash
  ssh username@your-server-ip
  ```

- [ ] **Update system**
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- [ ] **Install Python 3.11**
  ```bash
  sudo apt install python3.11 python3.11-venv python3-pip -y
  python3.11 --version
  ```

- [ ] **Install PostgreSQL**
  ```bash
  sudo apt install postgresql postgresql-contrib -y
  sudo systemctl start postgresql
  sudo systemctl enable postgresql
  ```

- [ ] **Create database**
  ```bash
  sudo -u postgres psql
  CREATE DATABASE ai_screener;
  CREATE USER screener_user WITH PASSWORD 'STRONG_PASSWORD_HERE';
  GRANT ALL PRIVILEGES ON DATABASE ai_screener TO screener_user;
  \q
  ```

- [ ] **Install Node.js & PM2**
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt install nodejs -y
  sudo npm install -g pm2
  pm2 --version
  ```

- [ ] **Install Nginx**
  ```bash
  sudo apt install nginx -y
  sudo systemctl start nginx
  sudo systemctl enable nginx
  ```

---

## 📦 APPLICATION DEPLOYMENT

- [ ] **Create application directory**
  ```bash
  sudo mkdir -p /var/www/ai-screener
  sudo chown $USER:$USER /var/www/ai-screener
  cd /var/www/ai-screener
  ```

- [ ] **Clone repository**
  ```bash
  git clone YOUR_REPO_URL .
  ```

- [ ] **Create virtual environment**
  ```bash
  python3.11 -m venv venv
  source venv/bin/activate
  ```

- [ ] **Install dependencies**
  ```bash
  pip install --upgrade pip
  pip install -r requirements_professional.txt
  ```

- [ ] **Create .env file**
  ```bash
  cp .env.example .env
  nano .env
  ```
  Fill in:
  - DHAN_CLIENT_ID
  - DHAN_ACCESS_TOKEN
  - DATABASE_URL

- [ ] **Initialize database**
  ```bash
  source venv/bin/activate
  python -c "from database.db_manager import get_db; db = get_db()"
  ```

- [ ] **Create logs directory**
  ```bash
  mkdir -p /var/www/ai-screener/logs
  ```

---

## 🚀 PM2 CONFIGURATION

- [ ] **Update ecosystem.config.js paths**
  - Check that paths match `/var/www/ai-screener`

- [ ] **Start with PM2**
  ```bash
  pm2 start ecosystem.config.js
  ```

- [ ] **Setup PM2 startup**
  ```bash
  pm2 startup
  # Run the command it outputs
  pm2 save
  ```

- [ ] **Verify PM2 status**
  ```bash
  pm2 status
  pm2 logs ai-screener-streamlit --lines 50
  ```

---

## 🌐 NGINX CONFIGURATION

- [ ] **Create Nginx config**
  ```bash
  sudo nano /etc/nginx/sites-available/ai-screener
  ```
  - Copy content from `nginx.conf` file
  - Update `server_name` with your domain/IP

- [ ] **Enable site**
  ```bash
  sudo ln -s /etc/nginx/sites-available/ai-screener /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```

- [ ] **Configure firewall**
  ```bash
  sudo ufw allow 'Nginx Full'
  sudo ufw allow OpenSSH
  sudo ufw enable
  ```

---

## 🔒 SSL SETUP (Optional but Recommended)

- [ ] **Install Certbot**
  ```bash
  sudo apt install certbot python3-certbot-nginx -y
  ```

- [ ] **Get SSL certificate**
  ```bash
  sudo certbot --nginx -d your-domain.com -d www.your-domain.com
  ```

- [ ] **Test auto-renewal**
  ```bash
  sudo certbot renew --dry-run
  ```

---

## ✅ VERIFICATION

- [ ] **Check all services running**
  ```bash
  pm2 status
  sudo systemctl status nginx
  sudo systemctl status postgresql
  ```

- [ ] **Test application access**
  - [ ] Open browser: http://your-domain.com
  - [ ] Dashboard loads correctly
  - [ ] Can navigate between pages
  - [ ] S&R Analysis works (single stock)
  - [ ] Batch Analysis works (multiple stocks)
  - [ ] No console errors

- [ ] **Check logs**
  ```bash
  pm2 logs ai-screener-streamlit --lines 100
  sudo tail -f /var/log/nginx/error.log
  ```

- [ ] **Test from different devices**
  - [ ] Desktop browser
  - [ ] Mobile browser
  - [ ] Different network

---

## 🔄 DEPLOYMENT SCRIPT

- [ ] **Make deploy script executable**
  ```bash
  chmod +x /var/www/ai-screener/deploy.sh
  ```

- [ ] **Test deployment script**
  ```bash
  ./deploy.sh
  ```

---

## 📊 MONITORING

- [ ] **Setup PM2 monitoring**
  ```bash
  pm2 monit
  ```

- [ ] **Check resource usage**
  ```bash
  htop
  df -h
  free -h
  ```

- [ ] **Setup log rotation** (optional)
  ```bash
  pm2 install pm2-logrotate
  pm2 set pm2-logrotate:max_size 10M
  pm2 set pm2-logrotate:retain 7
  ```

---

## 🎯 POST-DEPLOYMENT

- [ ] **Document server details**
  - Server IP: _________________
  - Domain: _________________
  - SSH username: _________________
  - Database password: _________________ (keep secure!)

- [ ] **Share access URL with team**
  - URL: http://your-domain.com

- [ ] **Setup monitoring alerts** (optional)
  - Uptime monitoring (UptimeRobot, Pingdom)
  - Server monitoring (New Relic, Datadog)

- [ ] **Backup strategy**
  - Database backups
  - Code repository up to date
  - .env file backed up securely

---

## 🐛 TROUBLESHOOTING

If something goes wrong:

1. **Check PM2 logs**
   ```bash
   pm2 logs ai-screener-streamlit --lines 100
   ```

2. **Check Nginx logs**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Restart services**
   ```bash
   pm2 restart ai-screener-streamlit
   sudo systemctl restart nginx
   ```

4. **Check if port is accessible**
   ```bash
   curl http://localhost:8501
   ```

5. **Verify database connection**
   ```bash
   psql -U screener_user -d ai_screener -h localhost
   ```

---

## 📞 QUICK COMMANDS

```bash
# View application status
pm2 status

# View logs
pm2 logs ai-screener-streamlit

# Restart application
pm2 restart ai-screener-streamlit

# Deploy updates
cd /var/www/ai-screener && ./deploy.sh

# Check nginx status
sudo systemctl status nginx

# Check database status
sudo systemctl status postgresql
```

---

## ✅ DEPLOYMENT COMPLETE!

Once all items are checked, your application is live! 🎉

**Access:** http://your-domain.com

**Next steps:**
1. Test all features
2. Share with users
3. Monitor logs for first 24 hours
4. Setup automated backups
5. Plan update schedule

---

**Happy Trading! 📈💰🚀**

