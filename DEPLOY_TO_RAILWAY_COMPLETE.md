# 🚂 Complete Railway Deployment Guide

## Quick Start (5 Minutes)

### Step 1: Create Railway Project
1. Go to https://railway.app
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository: `dubaiswarna/ai-screener-backup`
4. Railway creates a project

### Step 2: Add MySQL Database
1. In Railway project → **"+ New"** → **"Database"** → **"Add MySQL"**
2. Railway creates MySQL instance
3. **Copy connection details** (shown in MySQL service)

### Step 3: Configure Backend Service

Railway should auto-detect your repo. Configure it:

**Environment Variables** (Backend Service → Variables):
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
- **Root Directory**: `/` (or leave empty)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python api_server.py`

### Step 4: Configure Frontend Service

1. **"+ New"** → **"GitHub Repo"** → Select same repo
2. Railway creates second service

**Environment Variables** (Frontend Service → Variables):
```env
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app
NODE_ENV=production
PORT=${{PORT}}
```

**Settings**:
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`

### Step 5: Generate Domains

1. **Backend Service** → **Settings** → **Generate Domain**
   - Copy: `https://ai-screener-backend-xxxx.up.railway.app`

2. **Frontend Service** → **Settings** → **Generate Domain**
   - Copy: `https://ai-screener-frontend-xxxx.up.railway.app`

3. **Update Frontend Variable**:
   - Set `NEXT_PUBLIC_API_URL` to backend domain

### Step 6: Deploy

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "Configure Railway deployment"
   git push origin main
   ```

2. Railway auto-deploys
3. Check deployment logs
4. Visit your frontend URL!

---

## 📋 Complete Checklist

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] MySQL service added
- [ ] Backend service configured
- [ ] Frontend service configured
- [ ] Environment variables set
- [ ] Domains generated
- [ ] Backend URL added to frontend
- [ ] Code pushed to GitHub
- [ ] Deployment successful
- [ ] Backend health check passes
- [ ] Frontend loads correctly

---

## 🔧 Troubleshooting

### Database Connection Issues
- Verify MySQL service is running
- Check environment variables use `${{MySQL.*}}` syntax
- Review Railway logs for connection errors

### Frontend Can't Connect
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is deployed
- Test backend URL: `/health` endpoint

### Build Failures
- Check Railway build logs
- Verify `requirements.txt` and `package.json`
- Ensure Python 3.9+ and Node.js 18+

---

## 🎉 Success!

Your app is live at:
- **Frontend**: `https://your-frontend.up.railway.app`
- **Backend**: `https://your-backend.up.railway.app`
- **API Docs**: `https://your-backend.up.railway.app/docs`

**Auto-deployment**: Every push to GitHub triggers a new deployment!

