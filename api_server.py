"""
FastAPI Backend Server
======================
REST API for AI Trading System
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uvicorn
import logging
import asyncio
import json

# Import our modules
from database.db_manager import get_db
from risk_management.risk_engine import RiskEngine
from broker_integration.broker_client import get_broker_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db = None
risk_engine = None
broker_client = None

# ============================================================
# LIFESPAN EVENTS (Startup/Shutdown)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    global db, risk_engine, broker_client
    
    # Startup
    try:
        # Initialize database
        db = get_db()
        logger.info("✅ Database connected")
        
        # Initialize database tables if needed
        try:
            db.get_user_config()
        except Exception:
            logger.info("📊 Database tables will be initialized automatically by DatabaseManager")
            # Tables are created automatically in DatabaseManager._init_mysql() or _init_sqlite()
            
        # On Railway, ensure tables are created
        if os.getenv('RAILWAY_ENVIRONMENT'):
            logger.info("🚂 Running on Railway - ensuring database is initialized")
            try:
                db.get_user_config()
            except Exception:
                logger.info("📊 Initializing Railway MySQL database...")
                # Force table creation
                from database.mysql_manager import create_mysql_tables
                from config.db_config import MYSQL_CONFIG
                try:
                    import pymysql
                    # Use Railway MySQL env vars if available
                    railway_config = {
                        'host': os.getenv('MYSQLHOST') or MYSQL_CONFIG['host'],
                        'port': int(os.getenv('MYSQLPORT') or MYSQL_CONFIG['port']),
                        'user': os.getenv('MYSQLUSER') or MYSQL_CONFIG['user'],
                        'password': os.getenv('MYSQLPASSWORD') or MYSQL_CONFIG['password'],
                        'database': os.getenv('MYSQLDATABASE') or MYSQL_CONFIG['database'],
                        'charset': 'utf8mb4'
                    }
                    conn = pymysql.connect(**railway_config)
                    create_mysql_tables(conn)
                    conn.close()
                    logger.info("✅ Railway MySQL tables initialized")
                except Exception as init_error:
                    logger.warning(f"⚠️ Railway init error (will retry): {init_error}")
        
        # Get user config
        config = db.get_user_config()
        capital = config.get('total_capital', 1000000)
        
        # Initialize risk engine
        risk_engine = RiskEngine(total_capital=capital)
        logger.info(f"✅ Risk Engine initialized with ₹{capital:,.0f}")
        
        # Initialize broker (paper trading by default)
        broker_client = get_broker_client('paper')
        logger.info("✅ Broker client connected (Paper Trading)")
        
        logger.info("🚀 API Server started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    if db:
        db.close()
        logger.info("✅ Database connections closed")

# ============================================================
# FASTAPI APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="Professional AI Screener API",
    description="REST API for AI-powered stock screening and trading",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware (allow frontend to access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================

class SignalCreate(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "NSE_RELIANCE"})
    signal_type: str = Field(..., json_schema_extra={"example": "BUY"})
    confidence: float = Field(..., ge=0, le=100, json_schema_extra={"example": 85.5})
    entry_price: float = Field(..., gt=0, json_schema_extra={"example": 2450.00})
    target_price: Optional[float] = Field(None, json_schema_extra={"example": 2550.00})
    stop_loss: Optional[float] = Field(None, json_schema_extra={"example": 2400.00})
    model_name: Optional[str] = Field(None, json_schema_extra={"example": "xgb_NSE_RELIANCE"})
    signal_strength: Optional[str] = Field(None, json_schema_extra={"example": "STRONG"})
    volume: Optional[int] = Field(None, json_schema_extra={"example": 1000000})

class OrderCreate(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "NSE_RELIANCE"})
    transaction_type: str = Field(..., json_schema_extra={"example": "BUY"})
    quantity: int = Field(..., gt=0, json_schema_extra={"example": 10})
    order_type: str = Field(default="MARKET", json_schema_extra={"example": "MARKET"})
    price: Optional[float] = Field(None, json_schema_extra={"example": 2450.00})

class UserConfigUpdate(BaseModel):
    total_capital: Optional[float] = None
    max_risk_per_trade: Optional[float] = None
    max_portfolio_risk: Optional[float] = None
    min_confidence: Optional[float] = None


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Professional AI Screener API v3.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        if db and db.test_connection():
            status["services"]["database"] = "connected"
        else:
            status["services"]["database"] = "disconnected"
            status["status"] = "degraded"
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    # Check broker
    status["services"]["broker"] = "connected" if broker_client and broker_client.is_connected else "disconnected"
    
    # Check risk engine
    status["services"]["risk_engine"] = "active" if risk_engine else "inactive"
    
    return status

# ============================================================
# SIGNALS ENDPOINTS
# ============================================================

@app.get("/api/v1/signals", response_model=List[Dict])
async def get_signals(min_confidence: float = 0.0, limit: int = 100):
    """
    Get active signals.
    
    Args:
        min_confidence: Minimum confidence threshold (0-100)
        limit: Maximum number of signals to return
    """
    try:
        signals = db.get_active_signals(min_confidence=min_confidence)
        return signals[:limit]
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/signals", response_model=Dict)
async def create_signal(signal: SignalCreate):
    """Create a new trading signal."""
    try:
        # Calculate risk metrics
        if signal.stop_loss and risk_engine:
            position = risk_engine.calculate_position_size(
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                confidence=signal.confidence / 100
            )
            
            signal_data = {
                **signal.dict(),
                'risk_reward_ratio': position.get('risk_pct', 0),
                'position_size': position.get('position_size', 0),
                'max_risk_amount': position.get('risk_amount', 0),
                'valid_until': datetime.now() + timedelta(days=1)
            }
        else:
            signal_data = {
                **signal.dict(),
                'valid_until': datetime.now() + timedelta(days=1)
            }
        
        # Save to database
        signal_id = db.save_signal(signal_data)
        
        if signal_id:
            return {
                "status": "success",
                "signal_id": signal_id,
                "message": "Signal created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save signal")
            
    except Exception as e:
        logger.error(f"Error creating signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/signals/{symbol}")
async def get_signals_by_symbol(symbol: str, limit: int = 50):
    """Get signals for a specific symbol."""
    try:
        signals = db.get_signals_by_symbol(symbol, limit=limit)
        return signals
    except Exception as e:
        logger.error(f"Error getting signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# PORTFOLIO ENDPOINTS
# ============================================================

@app.get("/api/v1/portfolio")
async def get_portfolio():
    """Get current portfolio positions."""
    try:
        positions = db.get_portfolio()
        summary = db.get_portfolio_summary()
        
        return {
            "positions": positions,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/summary")
async def get_portfolio_summary():
    """Get portfolio summary statistics."""
    try:
        summary = db.get_portfolio_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# TRADES ENDPOINTS
# ============================================================

@app.get("/api/v1/trades")
async def get_trades(status: Optional[str] = None, days: int = 30):
    """
    Get trades.
    
    Args:
        status: Filter by status (OPEN, CLOSED, STOPPED, TARGET_HIT)
        days: Number of days of history
    """
    try:
        if status == "OPEN":
            trades = db.get_open_trades()
        else:
            trades = db.get_trade_history(days=days)
        
        return trades
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/trades")
async def create_trade(trade_data: Dict):
    """Create a new trade."""
    try:
        trade_id = db.save_trade(trade_data)
        if trade_id:
            return {"status": "success", "trade_id": trade_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to save trade")
    except Exception as e:
        logger.error(f"Error creating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ORDERS ENDPOINTS
# ============================================================

@app.post("/api/v1/orders")
async def place_order(order: OrderCreate):
    """
    Place an order.
    
    This will execute through the configured broker (Paper/Dhan/etc)
    """
    try:
        # Place order through broker
        order_result = broker_client.place_order(
            symbol=order.symbol,
            transaction_type=order.transaction_type,
            quantity=order.quantity,
            order_type=order.order_type,
            price=order.price
        )
        
        if order_result.get('status') in ['COMPLETE', 'SUCCESS']:
            # Save trade to database
            trade_data = {
                'symbol': order.symbol,
                'trade_type': order.transaction_type,
                'entry_price': order_result.get('price', order.price),
                'quantity': order.quantity,
                'entry_amount': order.quantity * order_result.get('price', order.price),
                'broker_order_id': order_result.get('order_id'),
                'notes': f"API order via {broker_client.name}"
            }
            
            trade_id = db.save_trade(trade_data)
            order_result['trade_id'] = trade_id
        
        return order_result
        
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# QUOTES ENDPOINTS
# ============================================================

@app.get("/api/v1/quotes/{symbol}")
async def get_quote(symbol: str):
    """Get current quote for a symbol."""
    try:
        quote = broker_client.get_quote(symbol)
        if quote:
            return quote
        else:
            raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
    except Exception as e:
        logger.error(f"Error getting quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    days: int = 30,
    interval: str = "1d"
):
    """
    Get historical data.
    
    Args:
        symbol: Stock symbol
        days: Number of days of history
        interval: Data interval (1m, 5m, 15m, 1h, 1d)
    """
    try:
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        
        df = broker_client.get_historical_data(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
        
        if not df.empty:
            return {
                "symbol": symbol,
                "data": df.to_dict(orient='records'),
                "count": len(df)
            }
        else:
            raise HTTPException(status_code=404, detail="No data found")
            
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# RISK MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/v1/risk/position-size")
async def calculate_position_size(
    entry_price: float,
    stop_loss: float,
    confidence: float = 75.0
):
    """Calculate optimal position size."""
    try:
        position = risk_engine.calculate_position_size(
            entry_price=entry_price,
            stop_loss=stop_loss,
            confidence=confidence / 100
        )
        return position
    except Exception as e:
        logger.error(f"Error calculating position size: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/risk/report")
async def get_risk_report():
    """Get comprehensive risk report."""
    try:
        # Get portfolio data
        positions = db.get_portfolio()
        
        # Get trade history for returns calculation
        trades = db.get_trade_history(days=90)
        
        # Calculate returns
        returns = []
        equity_curve = [risk_engine.total_capital]
        
        for trade in trades:
            if trade.get('profit_loss_pct'):
                returns.append(trade['profit_loss_pct'] / 100)
                equity_curve.append(equity_curve[-1] * (1 + returns[-1]))
        
        # Generate risk report
        report = risk_engine.generate_risk_report(
            positions=positions,
            returns=returns,
            equity_curve=equity_curve,
            price_history={}  # Can add price history if needed
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating risk report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# CONFIGURATION ENDPOINTS
# ============================================================

@app.get("/api/v1/config")
async def get_config():
    """Get user configuration."""
    try:
        config = db.get_user_config()
        return config
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/config")
async def update_config(config: UserConfigUpdate):
    """Update user configuration."""
    try:
        config_data = {k: v for k, v in config.dict().items() if v is not None}
        success = db.update_user_config(config_data)
        
        if success:
            # Update risk engine if capital changed
            if 'total_capital' in config_data:
                global risk_engine
                risk_engine = RiskEngine(total_capital=config_data['total_capital'])
            
            return {"status": "success", "message": "Configuration updated"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update config")
            
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# MODEL PERFORMANCE ENDPOINTS
# ============================================================

@app.get("/api/v1/models/performance")
async def get_model_performance(model_name: Optional[str] = None):
    """Get model performance metrics."""
    try:
        performance = db.get_model_performance(model_name=model_name)
        return performance
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ALERTS ENDPOINTS
# ============================================================

@app.get("/api/v1/alerts")
async def get_alerts(hours: int = 24):
    """Get recent alerts."""
    try:
        alerts = db.get_recent_alerts(hours=hours)
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# WEBSOCKET ENDPOINT (Real-time price updates)
# ============================================================

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/api/v1/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates.
    
    Send symbols as JSON: {"action": "subscribe", "symbols": ["RELIANCE", "TCS"]}
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive subscription request
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('action') == 'subscribe':
                symbols = message.get('symbols', [])
                
                # Stream prices for subscribed symbols
                for symbol in symbols:
                    quote = broker_client.get_quote(symbol)
                    await websocket.send_json({
                        'symbol': symbol,
                        'price': quote.get('ltp', 0),
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Wait a bit before next update
                await asyncio.sleep(1)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

# ============================================================
# STATISTICS ENDPOINTS
# ============================================================

@app.get("/api/v1/stats/overview")
async def get_stats_overview():
    """Get system overview statistics."""
    try:
        return {
            "signals": {
                "active": len(db.get_active_signals()),
                "total_today": len(db.get_active_signals())  # Can refine this
            },
            "portfolio": db.get_portfolio_summary(),
            "trades": {
                "open": len(db.get_open_trades()),
                "closed_30d": len(db.get_trade_history(days=30))
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    # Get port from environment (Railway sets PORT)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Detect if running on Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY")
    
    print("="*60)
    print("🚀 PROFESSIONAL AI SCREENER API v3.0")
    print("="*60)
    if is_railway:
        print("🚂 Running on Railway")
        public_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "https://your-app.up.railway.app")
        print(f"\n📊 API Documentation: {public_url}/docs")
        print(f"📊 Alternative docs: {public_url}/redoc")
        print(f"💚 Health check: {public_url}/health")
    else:
        print(f"\n📊 API Documentation: http://localhost:{port}/docs")
        print(f"📊 Alternative docs: http://localhost:{port}/redoc")
        print(f"💚 Health check: http://localhost:{port}/health")
    print("\n" + "="*60)
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=not is_railway,  # Disable reload on Railway
        log_level="info"
    )

