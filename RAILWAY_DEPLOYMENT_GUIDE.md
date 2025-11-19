# 🚂 Railway Deployment Guide - Complete Setup

## Overview

This guide will help you deploy the entire AI Screener project to Railway with:
- ✅ GitHub integration (auto-deploy)
- ✅ Next.js frontend
- ✅ FastAPI backend
- ✅ MySQL database (Railway MySQL)

---

## 📋 Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Repository**: Your code should be in a GitHub repo
3. **Railway CLI** (optional): `npm i -g @railway/cli`

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account
5. Select repository: `dubaiswarna/ai-screener-backup` (or your repo)
6. Railway will create a new project

### Step 2: Add MySQL Database Service

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add MySQL"**
3. Railway will create a MySQL instance
4. **Note the connection details** (you'll need these)

### Step 3: Configure Backend Service

1. Railway should auto-detect your project
2. If not, click **"+ New"** → **"GitHub Repo"** → Select your repo
3. Railway will create a service for your backend

#### Configure Backend Environment Variables:

In Railway → Your Backend Service → **Variables** tab, add:

```env
# Database Configuration
DB_TYPE=mysql
MYSQLHOST=${{MySQL.MYSQLHOST}}
MYSQLPORT=${{MySQL.MYSQLPORT}}
MYSQLUSER=${{MySQL.MYSQLUSER}}
MYSQLPASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQLDATABASE=${{MySQL.MYSQLDATABASE}}

# Or use explicit values (if Railway variables don't work)
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}

# Server Configuration
PORT=${{PORT}}
RAILWAY_ENVIRONMENT=production

# Python Configuration
PYTHONUNBUFFERED=1
```

**Important**: Railway MySQL service provides these variables automatically:
- `MYSQLHOST` - MySQL host
- `MYSQLPORT` - MySQL port
- `MYSQLUSER` - MySQL username
- `MYSQLPASSWORD` - MySQL password
- `MYSQLDATABASE` - MySQL database name

#### Configure Backend Build Settings:

1. Go to **Settings** → **Build Command**:
   ```
   pip install -r requirements.txt
   ```

2. **Start Command**:
   ```
   python api_server.py
   ```

3. **Root Directory**: Leave empty (or `/`)

### Step 4: Configure Frontend Service (Next.js)

1. Click **"+ New"** → **"GitHub Repo"** → Select same repo
2. Railway will create a second service

#### Configure Frontend Environment Variables:

```env
# Backend API URL (use Railway backend URL)
NEXT_PUBLIC_API_URL=${{BackendService.RAILWAY_PUBLIC_DOMAIN}}

# Or if backend is on different domain:
# NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app

# Node Configuration
NODE_ENV=production
PORT=${{PORT}}
```

#### Configure Frontend Build Settings:

1. **Root Directory**: `frontend`

2. **Build Command**:
   ```
   npm install && npm run build
   ```

3. **Start Command**:
   ```
   npm start
   ```

### Step 5: Generate Public Domain

1. For **Backend Service**:
   - Go to **Settings** → **Generate Domain**
   - Copy the domain (e.g., `ai-screener-backend.up.railway.app`)

2. For **Frontend Service**:
   - Go to **Settings** → **Generate Domain**
   - Copy the domain (e.g., `ai-screener-frontend.up.railway.app`)

3. **Update Frontend Environment Variable**:
   - Set `NEXT_PUBLIC_API_URL` to your backend domain:
   ```
   NEXT_PUBLIC_API_URL=https://ai-screener-backend.up.railway.app
   ```

### Step 6: Database Initialization

The database tables will be created automatically when the backend starts. The `api_server.py` includes initialization code that:

1. Connects to MySQL
2. Creates all required tables
3. Inserts default configuration

**Manual Initialization** (if needed):

1. Go to Railway → MySQL Service → **Connect** tab
2. Copy the connection command
3. Or use Railway's MySQL console
4. Run: `python railway-init.py` (if you add it to build)

### Step 7: Deploy and Test

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Configure for Railway deployment"
   git push origin main
   ```

2. **Railway will auto-deploy**:
   - Watch the deployment logs
   - Wait for build to complete
   - Check for any errors

3. **Test Backend**:
   - Visit: `https://your-backend-domain.up.railway.app/health`
   - Should return: `{"status": "healthy", ...}`

4. **Test Frontend**:
   - Visit: `https://your-frontend-domain.up.railway.app`
   - Should show the dashboard

---

## 🔧 Railway Configuration Files

### `railway-backend.toml`
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python api_server.py"
restartPolicyType = "on_failure"
healthcheckPath = "/health"
```

### `railway-frontend.toml`
```toml
[build]
builder = "nixpacks"
buildCommand = "cd frontend && npm install && npm run build"

[deploy]
startCommand = "cd frontend && npm start"
```

---

## 📝 Environment Variables Summary

### Backend Service Variables:
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

### Frontend Service Variables:
```env
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app
NODE_ENV=production
PORT=${{PORT}}
```

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

**Solution:**
1. Check MySQL service is running in Railway
2. Verify environment variables are set correctly
3. Check Railway logs for connection errors
4. Ensure `MYSQLHOST`, `MYSQLPORT`, etc. are using `${{MySQL.*}}` syntax

### Issue: Frontend Can't Connect to Backend

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check backend is deployed and running
3. Test backend URL directly: `https://backend-url/health`
4. Check CORS settings in `api_server.py`

### Issue: Build Fails

**Solution:**
1. Check build logs in Railway
2. Verify `requirements.txt` has all dependencies
3. Check `frontend/package.json` is correct
4. Ensure Python 3.9+ and Node.js 18+ are available

### Issue: Tables Not Created

**Solution:**
1. Check backend logs for initialization errors
2. Manually run: `python railway-init.py`
3. Verify MySQL credentials are correct
4. Check database permissions

---

## 🔄 Auto-Deployment Setup

Railway automatically deploys when you push to GitHub:

1. **Push to main branch**:
   ```bash
   git push origin main
   ```

2. **Railway detects changes**:
   - Starts building automatically
   - Deploys new version
   - Shows deployment status

3. **Monitor deployment**:
   - Go to Railway dashboard
   - Click on your service
   - View **Deployments** tab
   - Check logs for errors

---

## 📊 Service Architecture

```
GitHub Repo
    ↓
Railway Project
    ├── MySQL Service (Database)
    ├── Backend Service (FastAPI - Port 8000)
    └── Frontend Service (Next.js - Port 3000)
```

**Data Flow:**
```
User → Frontend (Next.js) → Backend API (FastAPI) → MySQL Database
```

---

## ✅ Deployment Checklist

- [ ] Railway project created
- [ ] MySQL service added and running
- [ ] Backend service configured
- [ ] Frontend service configured
- [ ] Environment variables set
- [ ] Public domains generated
- [ ] Backend domain added to frontend env
- [ ] Database tables created
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] GitHub auto-deploy working

---

## 🎉 Success!

Once deployed, your app will be available at:
- **Frontend**: `https://your-frontend-domain.up.railway.app`
- **Backend API**: `https://your-backend-domain.up.railway.app`
- **API Docs**: `https://your-backend-domain.up.railway.app/docs`

**Your AI Screener is now live on Railway!** 🚀

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Railway MySQL: https://docs.railway.app/databases/mysql
- Next.js Deployment: https://nextjs.org/docs/deployment

