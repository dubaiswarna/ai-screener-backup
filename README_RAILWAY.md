# 🚂 Railway Deployment - Quick Reference

## Your Railway App
**URL**: https://ai-screener-production-7319.up.railway.app/

## Architecture

```
GitHub Repo (dubaiswarna/ai-screener-backup)
    ↓
Railway Project
    ├── MySQL Service (Database)
    ├── Backend Service (FastAPI)
    └── Frontend Service (Next.js)
```

## Environment Variables

### Backend Service
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

### Frontend Service
```env
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app
NODE_ENV=production
PORT=${{PORT}}
```

## Quick Deploy

1. Push to GitHub:
   ```bash
   git push origin main
   ```

2. Railway auto-deploys

3. Check deployment logs in Railway dashboard

## Full Guide

See `RAILWAY_DEPLOYMENT_GUIDE.md` for complete instructions.

