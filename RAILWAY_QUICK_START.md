# 🚂 Railway Quick Start - 5 Minutes

## Your Railway App
**Current URL**: https://ai-screener-production-7319.up.railway.app/

## 🎯 What You Need to Do

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Configure Railway deployment with MySQL and Next.js"
git push origin main
```

### Step 2: Set Up Railway Services

#### A. Add MySQL Database
1. Railway Dashboard → Your Project → **"+ New"**
2. Select **"Database"** → **"Add MySQL"**
3. Railway creates MySQL instance automatically

#### B. Configure Backend Service

**Environment Variables** (Backend → Variables):
```env
DB_TYPE=mysql
MYSQLHOST=${{MySQL.MYSQLHOST}}
MYSQLPORT=${{MySQL.MYSQLPORT}}
MYSQLUSER=${{MySQL.MYSQLUSER}}
MYSQLPASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQLDATABASE=${{MySQL.MYSQLDATABASE}}
PORT=${{PORT}}
RAILWAY_ENVIRONMENT=production
```

**Settings**:
- Root Directory: `/` (or empty)
- Build Command: `pip install -r requirements.txt`
- Start Command: `python api_server.py`

#### C. Configure Frontend Service

1. **"+ New"** → **"GitHub Repo"** → Select same repo

**Environment Variables** (Frontend → Variables):
```env
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app
NODE_ENV=production
PORT=${{PORT}}
```

**Settings**:
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Start Command: `npm start`

#### D. Generate Domains

1. **Backend** → Settings → Generate Domain
2. **Frontend** → Settings → Generate Domain
3. Update `NEXT_PUBLIC_API_URL` in frontend with backend URL

### Step 3: Deploy

Railway auto-deploys on push. Monitor:
- Railway Dashboard → Deployments
- Check logs
- Verify health checks

---

## ✅ Verification

1. **Backend**: `https://backend-url/health` → Should return `{"status": "healthy"}`
2. **API Docs**: `https://backend-url/docs` → Interactive API docs
3. **Frontend**: `https://frontend-url` → Next.js dashboard
4. **Database**: Tables created automatically on first API call

---

## 📚 Full Guide

See `RAILWAY_DEPLOYMENT_GUIDE.md` for complete instructions.

---

## 🎉 Success!

Your app will be live at:
- **Frontend**: `https://your-frontend.up.railway.app`
- **Backend**: `https://your-backend.up.railway.app`

**Auto-deployment**: Every GitHub push triggers a new deployment!

