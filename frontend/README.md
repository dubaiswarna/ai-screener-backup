# AI Stock Screener - Next.js Frontend

Modern, responsive frontend for the AI Stock Screener built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 📊 **Dashboard** - Overview with statistics and recent signals
- 📈 **Signals** - View and create trading signals
- 💼 **Portfolio** - Track positions and P&L
- 📜 **Trades** - Complete trade history
- 🛡️ **Risk Report** - Comprehensive risk analysis
- ⚙️ **Settings** - Configure trading parameters

## Prerequisites

- Node.js 18+ and npm/yarn
- Python backend API running on `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Create `.env.local` file (optional, defaults to localhost:8000):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/              # Next.js app router pages
│   ├── page.tsx      # Dashboard
│   ├── signals/      # Signals page
│   ├── portfolio/    # Portfolio page
│   ├── trades/       # Trades page
│   ├── risk/         # Risk report page
│   └── settings/     # Settings page
├── components/       # React components
├── lib/              # Utilities and API client
└── public/           # Static assets
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default. Make sure:

1. The Python backend is running (`python api_server.py`)
2. CORS is enabled in the backend (already configured)
3. The API URL matches your backend configuration

## Building for Production

```bash
npm run build
npm start
```

## Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Charts (if needed)
- **Lucide React** - Icons
- **date-fns** - Date formatting

## Development

The app uses:
- Server Components by default
- Client Components (`'use client'`) for interactivity
- Automatic API route handling
- Optimized builds with Next.js

## Troubleshooting

**API Connection Issues:**
- Ensure the Python backend is running on port 8000
- Check CORS settings in `api_server.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**Build Errors:**
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

