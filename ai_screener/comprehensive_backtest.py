"""
COMPREHENSIVE 1-YEAR BACKTEST ENGINE
=====================================
Simulates AI Screener performance from Nov 2024 to Nov 2025
with ₹15L starting capital

Features:
- Full historical simulation using Excel data
- AI model signal generation
- Risk management (Kelly Criterion, position sizing)
- Drawdown tracking
- Performance metrics
- Problem period analysis
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================
# CONFIGURATION
# ============================================================

INITIAL_CAPITAL = 1500000  # ₹15 Lakhs
START_DATE = '2024-11-06'
END_DATE = '2025-11-05'
EXCEL_FILE = r"C:\python\MG AI\Nifty200_MASTER_10yeardata.xlsx"

# Risk Management Settings
MAX_POSITION_SIZE = 0.10  # Max 10% per position
CONFIDENCE_THRESHOLD = 0.75  # 75% minimum confidence
MAX_SIMULTANEOUS_POSITIONS = 15
STOP_LOSS_PCT = 0.03  # 3% stop loss
TARGET_PCT = 0.05  # 5% target

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=3600)
def load_excel_data():
    """Load historical data from Excel"""
    try:
        st.info("📂 Loading historical data from Excel...")
        
        # Read Excel file
        xls = pd.ExcelFile(EXCEL_FILE)
        
        all_data = {}
        for sheet_name in xls.sheet_names[:50]:  # Limit to 50 stocks for speed
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                
                # Standardize column names
                df.columns = df.columns.str.lower()
                
                if 'date' in df.columns and 'close' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # Filter date range
                    df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]
                    
                    if len(df) > 0:
                        all_data[sheet_name] = df
                        
            except Exception as e:
                continue
        
        st.success(f"✅ Loaded {len(all_data)} stocks with historical data")
        return all_data
        
    except Exception as e:
        st.error(f"❌ Error loading Excel: {e}")
        return {}

# ============================================================
# AI MODEL SIMULATION
# ============================================================

def simulate_ai_prediction(stock_data, date_idx):
    """
    Simulate AI model prediction for a given date
    Uses technical indicators to generate signals similar to real AI
    """
    if date_idx < 20:  # Need minimum history
        return None, 0.5
    
    # Get recent data
    recent = stock_data.iloc[max(0, date_idx-20):date_idx+1].copy()
    
    if len(recent) < 10:
        return None, 0.5
    
    # Calculate technical indicators
    close = recent['close'].values
    
    # RSI
    deltas = np.diff(close)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
    avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 0
    rs = avg_gain / avg_loss if avg_loss > 0 else 0
    rsi = 100 - (100 / (1 + rs)) if avg_loss > 0 else 50
    
    # Moving averages
    sma_10 = np.mean(close[-10:])
    sma_20 = np.mean(close[-20:]) if len(close) >= 20 else sma_10
    
    # Momentum
    momentum = (close[-1] - close[-5]) / close[-5] if len(close) >= 5 else 0
    
    # Generate signal
    bullish_score = 0
    bearish_score = 0
    
    # RSI signals
    if rsi < 30:
        bullish_score += 2
    elif rsi > 70:
        bearish_score += 2
    elif rsi < 45:
        bullish_score += 1
    elif rsi > 55:
        bearish_score += 1
    
    # MA signals
    if close[-1] > sma_10 > sma_20:
        bullish_score += 2
    elif close[-1] < sma_10 < sma_20:
        bearish_score += 2
    
    # Momentum
    if momentum > 0.02:
        bullish_score += 1
    elif momentum < -0.02:
        bearish_score += 1
    
    # Calculate confidence
    total_score = bullish_score + bearish_score
    if total_score == 0:
        return 'HOLD', 0.5
    
    if bullish_score > bearish_score:
        confidence = 0.5 + (bullish_score / (total_score * 2)) * 0.5
        return 'BUY', confidence
    elif bearish_score > bullish_score:
        confidence = 0.5 + (bearish_score / (total_score * 2)) * 0.5
        return 'SELL', confidence
    else:
        return 'HOLD', 0.5

# ============================================================
# RISK MANAGEMENT
# ============================================================

def calculate_position_size(capital, confidence, current_positions):
    """
    Calculate position size using Kelly Criterion
    """
    # Kelly fraction
    win_prob = confidence
    loss_prob = 1 - confidence
    win_loss_ratio = TARGET_PCT / STOP_LOSS_PCT
    
    kelly = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
    kelly = max(0, min(kelly, MAX_POSITION_SIZE))  # Cap at 10%
    
    # Adjust for current positions
    position_count = len(current_positions)
    if position_count >= MAX_SIMULTANEOUS_POSITIONS:
        return 0
    
    # Scale down if too many positions
    if position_count > 10:
        kelly *= 0.5
    
    position_value = capital * kelly
    return position_value

# ============================================================
# BACKTESTING ENGINE
# ============================================================

def run_backtest(stock_data_dict):
    """
    Run comprehensive backtest
    """
    st.info("🔄 Running backtest simulation...")
    
    # Get all unique dates
    all_dates = set()
    for stock_data in stock_data_dict.values():
        all_dates.update(stock_data['date'].dt.date)
    
    all_dates = sorted(list(all_dates))
    
    # Portfolio state
    capital = INITIAL_CAPITAL
    positions = {}  # symbol -> {entry_price, qty, entry_date, signal, confidence}
    closed_trades = []
    portfolio_history = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate day by day
    for day_idx, current_date in enumerate(all_dates):
        progress_bar.progress((day_idx + 1) / len(all_dates))
        status_text.text(f"📅 Simulating: {current_date}")
        
        # Check existing positions for stop-loss/target
        positions_to_close = []
        for symbol, pos in positions.items():
            if symbol not in stock_data_dict:
                continue
            
            stock_df = stock_data_dict[symbol]
            current_price_row = stock_df[stock_df['date'].dt.date == current_date]
            
            if len(current_price_row) == 0:
                continue
            
            current_price = current_price_row.iloc[0]['close']
            
            # Check stop-loss and target
            if pos['signal'] == 'BUY':
                pnl_pct = (current_price - pos['entry_price']) / pos['entry_price']
            else:  # SELL
                pnl_pct = (pos['entry_price'] - current_price) / pos['entry_price']
            
            # Exit conditions
            exit_reason = None
            if pnl_pct <= -STOP_LOSS_PCT:
                exit_reason = 'STOP_LOSS'
            elif pnl_pct >= TARGET_PCT:
                exit_reason = 'TARGET'
            elif (current_date - pos['entry_date']).days >= 20:  # Max holding 20 days
                exit_reason = 'TIME_STOP'
            
            if exit_reason:
                # Close position
                position_value = pos['entry_price'] * pos['qty']
                if pos['signal'] == 'BUY':
                    exit_value = current_price * pos['qty']
                else:
                    exit_value = position_value + (position_value - current_price * pos['qty'])
                
                pnl = exit_value - position_value
                capital += exit_value
                
                closed_trades.append({
                    'symbol': symbol,
                    'signal': pos['signal'],
                    'entry_date': pos['entry_date'],
                    'exit_date': current_date,
                    'entry_price': pos['entry_price'],
                    'exit_price': current_price,
                    'qty': pos['qty'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct * 100,
                    'exit_reason': exit_reason,
                    'confidence': pos['confidence']
                })
                
                positions_to_close.append(symbol)
        
        # Remove closed positions
        for symbol in positions_to_close:
            del positions[symbol]
        
        # Generate new signals
        for symbol, stock_df in stock_data_dict.items():
            if symbol in positions:
                continue  # Already have position
            
            # Get data up to current date
            historical = stock_df[stock_df['date'].dt.date <= current_date]
            
            if len(historical) < 20:
                continue
            
            # Get current date index
            date_idx = len(historical) - 1
            
            # Simulate AI prediction
            signal, confidence = simulate_ai_prediction(historical, date_idx)
            
            if signal in ['BUY', 'SELL'] and confidence >= CONFIDENCE_THRESHOLD:
                # Calculate position size
                position_value = calculate_position_size(capital, confidence, positions)
                
                if position_value < 1000:  # Minimum ₹1000
                    continue
                
                current_price = historical.iloc[-1]['close']
                qty = int(position_value / current_price)
                
                if qty == 0:
                    continue
                
                actual_position_value = current_price * qty
                
                if actual_position_value > capital:
                    continue  # Not enough capital
                
                # Open position
                capital -= actual_position_value
                positions[symbol] = {
                    'entry_price': current_price,
                    'qty': qty,
                    'entry_date': current_date,
                    'signal': signal,
                    'confidence': confidence
                }
        
        # Calculate portfolio value
        portfolio_value = capital
        for symbol, pos in positions.items():
            if symbol in stock_data_dict:
                stock_df = stock_data_dict[symbol]
                current_price_row = stock_df[stock_df['date'].dt.date == current_date]
                if len(current_price_row) > 0:
                    current_price = current_price_row.iloc[0]['close']
                    if pos['signal'] == 'BUY':
                        portfolio_value += current_price * pos['qty']
                    else:
                        position_value = pos['entry_price'] * pos['qty']
                        portfolio_value += position_value + (position_value - current_price * pos['qty'])
        
        portfolio_history.append({
            'date': current_date,
            'capital': capital,
            'positions_count': len(positions),
            'portfolio_value': portfolio_value
        })
    
    progress_bar.empty()
    status_text.empty()
    
    return closed_trades, portfolio_history

# ============================================================
# ANALYSIS & METRICS
# ============================================================

def calculate_metrics(closed_trades, portfolio_history):
    """
    Calculate performance metrics
    """
    if len(closed_trades) == 0:
        return None
    
    df_trades = pd.DataFrame(closed_trades)
    df_portfolio = pd.DataFrame(portfolio_history)
    
    # Basic metrics
    total_trades = len(df_trades)
    winning_trades = len(df_trades[df_trades['pnl'] > 0])
    losing_trades = len(df_trades[df_trades['pnl'] < 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = df_trades['pnl'].sum()
    avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = df_trades[df_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
    
    final_value = df_portfolio.iloc[-1]['portfolio_value']
    total_return = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    
    # Drawdown calculation
    df_portfolio['peak'] = df_portfolio['portfolio_value'].cummax()
    df_portfolio['drawdown'] = (df_portfolio['portfolio_value'] - df_portfolio['peak']) / df_portfolio['peak'] * 100
    max_drawdown = df_portfolio['drawdown'].min()
    
    # Monthly returns
    df_portfolio['date'] = pd.to_datetime(df_portfolio['date'])
    df_portfolio['month'] = df_portfolio['date'].dt.to_period('M')
    monthly_returns = df_portfolio.groupby('month').agg({
        'portfolio_value': ['first', 'last']
    })
    monthly_returns['return'] = ((monthly_returns[('portfolio_value', 'last')] - 
                                  monthly_returns[('portfolio_value', 'first')]) / 
                                 monthly_returns[('portfolio_value', 'first')] * 100)
    
    # Sharpe ratio (simplified)
    returns = df_portfolio['portfolio_value'].pct_change().dropna()
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0
    
    # Exit reason breakdown
    exit_reasons = df_trades['exit_reason'].value_counts()
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'final_value': final_value,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe,
        'df_trades': df_trades,
        'df_portfolio': df_portfolio,
        'monthly_returns': monthly_returns,
        'exit_reasons': exit_reasons
    }

# ============================================================
# STREAMLIT UI
# ============================================================

def main():
    st.set_page_config(page_title="AI Screener 1-Year Backtest", layout="wide", page_icon="📊")
    
    st.title("📊 COMPREHENSIVE 1-YEAR BACKTEST")
    st.markdown("### Simulating ₹15L Investment (Nov 2024 - Nov 2025)")
    st.markdown("---")
    
    # Settings
    with st.expander("⚙️ Backtest Settings", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Initial Capital", f"₹{INITIAL_CAPITAL:,.0f}")
            st.metric("Period", f"{START_DATE} to {END_DATE}")
        with col2:
            st.metric("Confidence Threshold", f"{CONFIDENCE_THRESHOLD*100:.0f}%")
            st.metric("Max Positions", MAX_SIMULTANEOUS_POSITIONS)
        with col3:
            st.metric("Stop Loss", f"{STOP_LOSS_PCT*100:.1f}%")
            st.metric("Target", f"{TARGET_PCT*100:.1f}%")
    
    # Load data
    stock_data = load_excel_data()
    
    if len(stock_data) == 0:
        st.error("❌ No data loaded. Please check Excel file.")
        return
    
    # Run backtest button
    if st.button("🚀 RUN BACKTEST", type="primary"):
        with st.spinner("Running comprehensive backtest..."):
            closed_trades, portfolio_history = run_backtest(stock_data)
            
            if len(closed_trades) == 0:
                st.warning("⚠️ No trades executed during backtest period")
                return
            
            # Calculate metrics
            metrics = calculate_metrics(closed_trades, portfolio_history)
            
            st.success("✅ Backtest Complete!")
            st.markdown("---")
            
            # ============================================================
            # PERFORMANCE OVERVIEW
            # ============================================================
            
            st.header("📈 Performance Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Final Portfolio Value", 
                         f"₹{metrics['final_value']:,.0f}",
                         f"{metrics['total_return']:+.2f}%")
            with col2:
                st.metric("Total P&L", 
                         f"₹{metrics['total_pnl']:,.0f}",
                         f"{metrics['total_return']:+.2f}%")
            with col3:
                st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
            with col4:
                st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Trades", metrics['total_trades'])
            with col2:
                st.metric("Winning Trades", metrics['winning_trades'])
            with col3:
                st.metric("Losing Trades", metrics['losing_trades'])
            with col4:
                st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
            
            st.markdown("---")
            
            # ============================================================
            # PORTFOLIO GROWTH CHART
            # ============================================================
            
            st.header("📊 Portfolio Growth Over Time")
            
            df_chart = metrics['df_portfolio'].copy()
            df_chart['date'] = pd.to_datetime(df_chart['date'])
            df_chart = df_chart.set_index('date')
            
            st.line_chart(df_chart['portfolio_value'])
            
            st.markdown("---")
            
            # ============================================================
            # DRAWDOWN ANALYSIS
            # ============================================================
            
            st.header("⚠️ Drawdown Analysis (Problem Periods)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Maximum Drawdown", f"{metrics['max_drawdown']:.2f}%")
                worst_dd_date = df_chart['drawdown'].idxmin()
                st.info(f"📅 Worst drawdown on: {worst_dd_date.strftime('%Y-%m-%d')}")
            
            with col2:
                st.line_chart(df_chart['drawdown'])
            
            st.markdown("---")
            
            # ============================================================
            # TRADE ANALYSIS
            # ============================================================
            
            st.header("💼 Trade Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Exit Reasons")
                st.bar_chart(metrics['exit_reasons'])
            
            with col2:
                st.subheader("Win/Loss Distribution")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Avg Win", f"₹{metrics['avg_win']:,.0f}")
                with col_b:
                    st.metric("Avg Loss", f"₹{metrics['avg_loss']:,.0f}")
                
                profit_factor = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] != 0 else 0
                st.metric("Profit Factor", f"{profit_factor:.2f}")
            
            st.markdown("---")
            
            # ============================================================
            # MONTHLY RETURNS
            # ============================================================
            
            st.header("📅 Monthly Returns")
            monthly_df = metrics['monthly_returns'].copy()
            monthly_df.index = monthly_df.index.astype(str)
            st.bar_chart(monthly_df['return'])
            
            st.markdown("---")
            
            # ============================================================
            # ALL TRADES TABLE
            # ============================================================
            
            st.header("📋 All Trades")
            
            df_display = metrics['df_trades'].copy()
            df_display = df_display.sort_values('pnl', ascending=False)
            df_display['entry_price'] = df_display['entry_price'].apply(lambda x: f"₹{x:,.2f}")
            df_display['exit_price'] = df_display['exit_price'].apply(lambda x: f"₹{x:,.2f}")
            df_display['pnl'] = df_display['pnl'].apply(lambda x: f"₹{x:,.0f}")
            df_display['pnl_pct'] = df_display['pnl_pct'].apply(lambda x: f"{x:+.2f}%")
            df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x*100:.1f}%")
            
            st.dataframe(df_display[['symbol', 'signal', 'entry_date', 'exit_date', 
                                     'entry_price', 'exit_price', 'qty', 'pnl', 
                                     'pnl_pct', 'exit_reason', 'confidence']], 
                        use_container_width=True, height=500)
            
            st.markdown("---")
            
            # ============================================================
            # RISK MANAGEMENT SUMMARY
            # ============================================================
            
            st.header("🛡️ Risk Management Summary")
            
            stop_loss_hits = len(df_display[df_display['exit_reason'] == 'STOP_LOSS'])
            target_hits = len(df_display[df_display['exit_reason'] == 'TARGET'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Stop Loss Hits", stop_loss_hits)
            with col2:
                st.metric("Target Hits", target_hits)
            with col3:
                risk_reward = target_hits / stop_loss_hits if stop_loss_hits > 0 else 0
                st.metric("Target/StopLoss Ratio", f"{risk_reward:.2f}")
            
            st.markdown("---")
            st.success("✅ Backtest analysis complete!")

if __name__ == "__main__":
    main()

