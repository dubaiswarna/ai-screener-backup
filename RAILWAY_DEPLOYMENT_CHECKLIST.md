# ✅ Railway Deployment Checklist

## Pre-Deployment

- [x] ✅ MySQL connector installed (`pymysql`)
- [x] ✅ Database configuration updated for Railway
- [x] ✅ API server configured for Railway PORT
- [x] ✅ Next.js frontend configured for Railway
- [x] ✅ Environment variable templates created
- [x] ✅ Database initialization scripts ready
- [x] ✅ Railway configuration files created

---

## Railway Setup Steps

### 1. Create Railway Project
- [ ] Go to https://railway.app
- [ ] Click **"New Project"**
- [ ] Select **"Deploy from GitHub repo"**
- [ ] Connect GitHub account
- [ ] Select repository: `dubaiswarna/ai-screener-backup`

### 2. Add MySQL Database Service
- [ ] Click **"+ New"** → **"Database"** → **"Add MySQL"**
- [ ] Wait for MySQL to be created
- [ ] Note: Railway provides connection variables automatically

### 3. Configure Backend Service

**Service Settings:**
- [ ] Root Directory: `/` (or leave empty)
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python api_server.py`

**Environment Variables** (Backend → Variables tab):
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

### 4. Configure Frontend Service

**Create Service:**
- [ ] Click **"+ New"** → **"GitHub Repo"** → Select same repo
- [ ] Railway creates second service

**Service Settings:**
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm install && npm run build`
- [ ] Start Command: `npm start`

**Environment Variables** (Frontend → Variables tab):
```env
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app
NODE_ENV=production
PORT=${{PORT}}
```

**Important**: Replace `your-backend-service.up.railway.app` with your actual backend domain after generating it.

### 5. Generate Public Domains

**Backend Domain:**
- [ ] Go to Backend Service → **Settings** → **Generate Domain**
- [ ] Copy domain: `https://ai-screener-backend-xxxx.up.railway.app`

**Frontend Domain:**
- [ ] Go to Frontend Service → **Settings** → **Generate Domain**
- [ ] Copy domain: `https://ai-screener-frontend-xxxx.up.railway.app`

**Update Frontend Variable:**
- [ ] Go to Frontend Service → **Variables**
- [ ] Update `NEXT_PUBLIC_API_URL` with backend domain
- [ ] Save

### 6. Deploy

- [ ] Push code to GitHub:
  ```bash
  git add .
  git commit -m "Configure Railway deployment"
  git push origin main
  ```

- [ ] Railway auto-deploys (watch logs)
- [ ] Wait for build to complete
- [ ] Check for errors in deployment logs

### 7. Verify Deployment

**Backend Verification:**
- [ ] Visit: `https://backend-url/health`
- [ ] Should return: `{"status": "healthy", ...}`
- [ ] Visit: `https://backend-url/docs`
- [ ] Should show FastAPI interactive docs

**Frontend Verification:**
- [ ] Visit: `https://frontend-url`
- [ ] Should load Next.js dashboard
- [ ] Check browser console for errors
- [ ] Verify API calls work

**Database Verification:**
- [ ] Check backend logs for "Database tables initialized"
- [ ] Or visit: `https://backend-url/api/v1/stats/overview`
- [ ] Should return data (even if empty)

---

## 🐛 Troubleshooting

### Database Connection Failed
- Check MySQL service is running
- Verify environment variables use `${{MySQL.*}}` syntax
- Check Railway logs for connection errors

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is deployed and running
- Test backend URL: `/health` endpoint
- Check CORS settings

### Build Fails
- Check Railway build logs
- Verify `requirements.txt` has all dependencies
- Check `frontend/package.json` is correct
- Ensure Python 3.9+ and Node.js 18+

### Tables Not Created
- Check backend logs for initialization
- Verify MySQL credentials
- Check database permissions
- Tables create automatically on first API call

---

## 📊 Service Architecture

```
GitHub Repo (dubaiswarna/ai-screener-backup)
    ↓
Railway Project
    ├── MySQL Service (Database)
    │   └── Auto-provides: MYSQLHOST, MYSQLPORT, etc.
    ├── Backend Service (FastAPI)
    │   └── Port: Railway assigns automatically
    └── Frontend Service (Next.js)
        └── Port: Railway assigns automatically
```

---

## 🎉 Success Criteria

- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Database tables created
- [ ] API endpoints respond correctly
- [ ] Frontend can fetch data from backend
- [ ] GitHub auto-deployment working

---

## 📝 Next Steps After Deployment

1. **Test All Features**:
   - Create a signal
   - View portfolio
   - Check trades
   - View risk report

2. **Monitor**:
   - Railway dashboard for resource usage
   - Deployment logs for errors
   - Application performance

3. **Update**:
   - Push changes to GitHub
   - Railway auto-deploys
   - Monitor deployment

---

## 📚 Documentation

- **Complete Guide**: `RAILWAY_DEPLOYMENT_GUIDE.md`
- **Quick Start**: `RAILWAY_QUICK_START.md`
- **Environment Variables**: `railway.env.example`

---

**Your project is ready for Railway!** 🚂

