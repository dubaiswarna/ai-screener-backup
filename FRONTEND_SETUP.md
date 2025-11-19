# 🚀 Next.js Frontend Setup Guide

## ✅ What's Been Created

A complete Next.js 14 frontend application with:

- **Modern UI** - Built with Tailwind CSS and responsive design
- **TypeScript** - Full type safety
- **6 Main Pages**:
  - Dashboard (overview with stats)
  - Signals (view/create trading signals)
  - Portfolio (positions and P&L)
  - Trades (trade history)
  - Risk Report (risk analysis)
  - Settings (configuration)

## 📋 Quick Start

### Option 1: Start Both Backend + Frontend (Recommended)

Double-click: `START_BOTH.bat`

This will:
1. Start the Python FastAPI backend on port 8000
2. Start the Next.js frontend on port 3000
3. Open both in separate windows

### Option 2: Start Separately

**Backend only:**
```bash
START_BACKEND.bat
```

**Frontend only:**
```bash
START_FRONTEND.bat
```

### Option 3: Manual Start

**1. Start Backend:**
```bash
cd C:\python\ai-screener
.\venv\Scripts\Activate.ps1
python api_server.py
```

**2. Start Frontend (in new terminal):**
```bash
cd C:\python\ai-screener\frontend
npm install  # First time only
npm run dev
```

## 🌐 Access URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js pages (App Router)
│   ├── page.tsx           # Dashboard
│   ├── signals/           # Signals page
│   ├── portfolio/         # Portfolio page
│   ├── trades/            # Trades page
│   ├── risk/              # Risk report page
│   └── settings/          # Settings page
├── components/            # React components
│   ├── Navigation.tsx
│   ├── Dashboard.tsx
│   ├── StatsCards.tsx
│   ├── SignalCard.tsx
│   └── CreateSignalForm.tsx
├── lib/
│   └── api.ts             # API client (connects to FastAPI)
├── package.json           # Dependencies
└── README.md              # Frontend documentation
```

## 🔧 Configuration

### Environment Variables

Create `frontend/.env.local` (optional):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Default is `http://localhost:8000` if not set.

## 📦 Dependencies

All dependencies are in `frontend/package.json`:

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons
- **date-fns** - Date formatting

## 🎨 Features

### Dashboard
- Real-time statistics cards
- Recent high-confidence signals
- Auto-refresh every 30-60 seconds

### Signals Page
- View all active signals
- Filter by confidence level
- Create new signals
- Signal cards with details

### Portfolio Page
- Current positions table
- Portfolio summary cards
- Real-time P&L updates
- Auto-refresh every 30 seconds

### Trades Page
- Complete trade history
- Filter by time period
- Status indicators
- P&L tracking

### Risk Report
- Risk level indicator
- Key metrics (Sharpe, Sortino, VaR)
- Portfolio heat analysis
- Performance summary

### Settings
- Configure capital
- Set risk parameters
- Minimum confidence threshold
- Save preferences

## 🔌 API Integration

The frontend connects to your FastAPI backend:

- **Base URL:** `http://localhost:8000`
- **Endpoints:** All `/api/v1/*` endpoints
- **CORS:** Already configured in backend
- **WebSocket:** Available for real-time prices (future enhancement)

## 🛠️ Development

### Install Dependencies
```bash
cd frontend
npm install
```

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Lint Code
```bash
npm run lint
```

## 🐛 Troubleshooting

### Frontend won't start
1. Make sure Node.js 18+ is installed: `node --version`
2. Install dependencies: `cd frontend && npm install`
3. Check for port conflicts (3000)

### API connection errors
1. Ensure backend is running: `python api_server.py`
2. Check backend URL in `.env.local`
3. Verify CORS is enabled in `api_server.py`

### Build errors
1. Clear cache: `rm -rf frontend/.next`
2. Reinstall: `rm -rf frontend/node_modules && npm install`

## 📝 Next Steps

1. **Start the backend:** `START_BACKEND.bat` or `python api_server.py`
2. **Start the frontend:** `START_FRONTEND.bat` or `cd frontend && npm run dev`
3. **Open browser:** http://localhost:3000
4. **Explore:** Navigate through all pages

## 🎉 You're Ready!

Your Next.js frontend is fully set up and ready to use. The UI is modern, responsive, and connects seamlessly to your Python backend.

**Happy Trading! 📈💰**

