"""
Backtest Dashboard - HYBRID MODE (AI + Technical)
==================================================
Uses AI models first, falls back to technical analysis
Shows signal source for each trade
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Complete Nifty 200 stocks
NIFTY200_STOCKS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'ITC',
    'LT', 'AXISBANK', 'ASIANPAINT', 'BAJFINANCE', 'MARUTI',
    'HCLTECH', 'WIPRO', 'TITAN', 'SUNPHARMA', 'NESTLEIND',
    'ULTRACEMCO', 'M&M', 'NTPC', 'POWERGRID', 'ONGC',
    'TATASTEEL', 'TECHM', 'ADANIPORTS', 'JSWSTEEL', 'BAJAJFINSV',
    'INDUSINDBK', 'COALINDIA', 'DIVISLAB', 'GRASIM', 'HINDALCO',
    'BRITANNIA', 'DRREDDY', 'SHREECEM', 'EICHERMOT', 'CIPLA',
    'TATACONSUM', 'HEROMOTOCO', 'UPL', 'APOLLOHOSP', 'BPCL',
    'BAJAJ-AUTO', 'TATAMOTORS', 'ADANIENT', 'SBILIFE', 'HDFCLIFE',
    'SIEMENS', 'DLF', 'AMBUJACEM', 'INDIGO', 'GODREJCP',
    'PIIND', 'PIDILITIND', 'BOSCHLTD', 'HAVELLS', 'BERGEPAINT',
    'TORNTPHARM', 'ABB', 'DMART', 'DABUR', 'BANDHANBNK',
    'TRENT', 'MARICO', 'GAIL', 'TVSMOTOR', 'COLPAL',
    'LUPIN', 'SRF', 'VEDL', 'OFSS', 'INDUSTOWER',
    'HINDPETRO', 'SBICARD', 'ADANIGREEN', 'MOTHERSON', 'ALKEM',
    'ABCAPITAL', 'ESCORTS', 'PERSISTENT', 'PAGEIND', 'MPHASIS',
    'BIOCON', 'CONCOR', 'IRCTC', 'ABFRL', 'ASTRAL',
    'CANBK', 'APOLLOTYRE', 'AUBANK', 'AUROPHARMA', 'BALKRISIND',
    'BATAINDIA', 'BEL', 'BHEL', 'CUMMINSIND', 'DELTACORP',
    'DIXON', 'FEDERALBNK', 'GLENMARK', 'HONAUT', 'IDFCFIRSTB',
    'INDHOTEL', 'JINDALSTEL', 'JUBLFOOD', 'LICHSGFIN', 'MANAPPURAM',
    'MRF', 'NMDC', 'OBEROIRLTY', 'OIL', 'PNB',
    'POLYCAB', 'RECLTD', 'TATACOMM', 'VOLTAS', 'WHIRLPOOL',
    'CHAMBLFERT', 'CHOLAFIN', 'COFORGE', 'COROMANDEL', 'CROMPTON',
    'GNFC', 'GODREJPROP', 'IIFL', 'IOC', 'IRFC',
    'JKCEMENT', 'LTTS', 'LAURUSLABS', 'MFSL', 'MGL',
    'NATIONALUM', 'NAUKRI', 'NAVINFLUOR', 'PAYTM', 'PETRONET',
    'PFC', 'SAIL', 'TATAPOWER', 'ZYDUSLIFE', 'AARTIIND',
    'ABBOTINDIA', 'ACC', 'ADANIPOWER', 'AJANTPHARM', 'APLLTD',
    'APLAPOLLO', 'ASHOKLEY', 'ATUL', 'EXIDEIND', 'CUB',
    'GRANULES', 'HATSUN', 'HINDCOPPER', 'ICICIPRULI', 'IDEA',
    'INTELLECT', 'KPITTECH', 'LTIM', 'M&MFIN', 'MRPL',
    'MUTHOOTFIN', 'NLCINDIA', 'PHOENIXLTD', 'PNBHOUSING', 'PRESTIGE',
    'PVR', 'RBLBANK', 'SANOFI', 'SCHAEFFLER', 'SONACOMS',
    'SUNDARMFIN', 'SUNDRMFAST', 'SUPREMEIND', 'TATACHEM', 'TATAELXSI',
    'TVSHLD', 'UNIONBANK', 'UNITDSPR', 'ZEEL'
]


class HybridBacktestEngine:
    """Hybrid backtesting: AI models + Technical analysis fallback."""
    
    def __init__(self, investment, max_portfolio, target, stop, max_days, ai_confidence_threshold=60):
        self.investment = investment
        self.max_portfolio = max_portfolio
        self.target = target
        self.stop = stop
        self.max_days = max_days
        self.ai_threshold = ai_confidence_threshold
        self.portfolio = []
        self.trades = []
        self.daily_values = []
        self.signal_stats = {'AI': 0, 'Technical': 0}
    
    def load_ai_model(self, symbol):
        """Load AI model for a stock."""
        model_path = Path(f"../Nifty200_Models_Pro/ensemble_{symbol}.pkl")
        if not model_path.exists():
            return None
        try:
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        except:
            return None
    
    def calculate_ai_features(self, df):
        """Calculate 89 features for AI model."""
        features = {}
        close = df['Close']
        
        # Price features
        features['close'] = close.iloc[-1]
        features['volume'] = df['Volume'].iloc[-1]
        
        # Moving averages
        for period in [5, 10, 20, 50, 100, 200]:
            if len(df) >= period:
                features[f'sma_{period}'] = close.rolling(period).mean().iloc[-1]
                features[f'ema_{period}'] = close.ewm(span=period).mean().iloc[-1]
            else:
                features[f'sma_{period}'] = close.mean()
                features[f'ema_{period}'] = close.mean()
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        features['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        features['macd'] = macd.iloc[-1]
        features['macd_signal'] = signal.iloc[-1]
        features['macd_hist'] = (macd - signal).iloc[-1]
        
        # Bollinger Bands
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        features['bb_upper'] = (sma20 + 2 * std20).iloc[-1]
        features['bb_lower'] = (sma20 - 2 * std20).iloc[-1]
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - close.shift())
        low_close = abs(df['Low'] - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        features['atr'] = true_range.rolling(14).mean().iloc[-1]
        
        # Volume
        features['volume_sma'] = df['Volume'].rolling(20).mean().iloc[-1]
        features['volume_ratio'] = features['volume'] / features['volume_sma'] if features['volume_sma'] > 0 else 1
        
        # Momentum
        features['momentum_5'] = close.pct_change(5).iloc[-1] * 100
        features['momentum_10'] = close.pct_change(10).iloc[-1] * 100
        features['momentum_20'] = close.pct_change(20).iloc[-1] * 100
        
        # Price position
        if len(df) >= 252:
            features['price_to_52w_high'] = (close.iloc[-1] / df['High'].rolling(252).max().iloc[-1]) * 100
            features['price_to_52w_low'] = (close.iloc[-1] / df['Low'].rolling(252).min().iloc[-1]) * 100
        else:
            features['price_to_52w_high'] = 100
            features['price_to_52w_low'] = 100
        
        # Pad to 89
        for i in range(len(features), 89):
            features[f'feature_{i}'] = 0
        
        return features
    
    def try_ai_signal(self, symbol, df):
        """Try to get signal from AI model."""
        model_data = self.load_ai_model(symbol)
        if not model_data:
            return False, 0, "No AI model"
        
        try:
            features = self.calculate_ai_features(df)
            feature_cols = model_data.get('feature_cols', [])
            if not feature_cols:
                return False, 0, "No feature columns"
            
            feature_values = [features.get(col, 0) for col in feature_cols]
            feature_vector = np.array([feature_values])
            
            xgb_model = model_data.get('xgb_model')
            lgb_model = model_data.get('lgb_model')
            
            if not xgb_model or not lgb_model:
                return False, 0, "Models not found"
            
            xgb_pred = xgb_model.predict_proba(feature_vector)[0]
            lgb_pred = lgb_model.predict_proba(feature_vector)[0]
            
            avg_proba = (xgb_pred + lgb_pred) / 2
            prediction = np.argmax(avg_proba)
            confidence = avg_proba[prediction] * 100
            
            # 0=SELL, 1=HOLD, 2=BUY
            if prediction == 2 and confidence >= self.ai_threshold:
                return True, confidence, "AI Model (XGBoost+LightGBM)"
            
            return False, confidence, f"AI confidence too low ({confidence:.1f}%)"
        
        except Exception as e:
            return False, 0, f"AI error: {str(e)}"
    
    def calculate_technical_signal(self, df):
        """Technical analysis fallback."""
        try:
            if len(df) < 50:
                return False, 0, "Insufficient data"
            
            close = df['Close']
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            
            # Avoid division by zero
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Check for NaN
            if pd.isna(current_rsi):
                return False, 0, "RSI calculation failed"
            
            sma_20 = close.rolling(20).mean()
            sma_50 = close.rolling(50).mean()
            
            current_price = close.iloc[-1]
            current_sma20 = sma_20.iloc[-1]
            current_sma50 = sma_50.iloc[-1]
            prev_sma20 = sma_20.iloc[-2]
            prev_sma50 = sma_50.iloc[-2]
            
            # Check for NaN in moving averages
            if pd.isna(current_sma20) or pd.isna(current_sma50):
                return False, 0, "MA calculation failed"
            
            # Golden Cross
            if (current_sma20 > current_sma50 and prev_sma20 <= prev_sma50 and 
                current_rsi < 40 and current_price > current_sma20):
                return True, 85, "Technical: Golden Cross + RSI Oversold"
            
            # Uptrend
            elif (current_price > current_sma20 and current_price > current_sma50 and
                  30 < current_rsi < 70 and current_sma20 > current_sma50):
                return True, 75, "Technical: Uptrend + Healthy RSI"
            
            # Pullback
            elif (current_sma20 > current_sma50 and 
                  abs(current_price - current_sma20) / current_sma20 < 0.02 and
                  current_rsi < 50):
                return True, 70, "Technical: Pullback to SMA20"
            
            return False, 0, "No technical signal"
        
        except Exception as e:
            return False, 0, f"Technical error: {str(e)}"
    
    def enter_position(self, symbol, date, price, reason, confidence, source):
        qty = int(self.investment / price)
        pos = {
            'symbol': symbol,
            'entry_date': date,
            'entry_price': price,
            'qty': qty,
            'investment': qty * price,
            'reason': reason,
            'confidence': confidence,
            'source': source,
            'target': price * (1 + self.target),
            'stop': price * (1 - self.stop),
            'max_date': date + timedelta(days=self.max_days)
        }
        self.portfolio.append(pos)
        return pos
    
    def check_exit(self, pos, date, price):
        if price >= pos['target']:
            return 'TARGET', price
        if price <= pos['stop']:
            return 'STOP_LOSS', price
        if date >= pos['max_date']:
            return 'TIME_EXIT', price
        return None, None
    
    def exit_position(self, pos, date, price, reason):
        exit_value = pos['qty'] * price
        pnl = exit_value - pos['investment']
        pnl_pct = (pnl / pos['investment']) * 100
        days = (date - pos['entry_date']).days
        
        trade = {
            'Symbol': pos['symbol'],
            'Entry_Date': pos['entry_date'],
            'Entry_Price': pos['entry_price'],
            'Exit_Date': date,
            'Exit_Price': price,
            'Exit_Reason': reason,
            'Investment': pos['investment'],
            'Exit_Value': exit_value,
            'PnL': pnl,
            'Return_%': pnl_pct,
            'Holding_Days': days,
            'Signal_Source': pos['source'],
            'Entry_Reason': pos['reason'],
            'Confidence': pos['confidence']
        }
        self.trades.append(trade)
        return trade
    
    def calculate_portfolio_value(self, date, stock_data):
        total = 0
        for pos in self.portfolio:
            if pos['symbol'] in stock_data:
                df = stock_data[pos['symbol']]
                day_data = df[df['Date'] == date]
                if not day_data.empty:
                    total += pos['qty'] * day_data['Close'].iloc[0]
        return total
    
    def run_backtest(self, stock_data, start_date, end_date):
        all_dates = sorted(set([d for df in stock_data.values() for d in df['Date']]))
        all_dates = [d for d in all_dates if start_date <= d <= end_date]
        
        for current_date in all_dates:
            # Check exits
            to_exit = []
            for pos in self.portfolio:
                if pos['symbol'] not in stock_data:
                    continue
                day_data = stock_data[pos['symbol']][stock_data[pos['symbol']]['Date'] == current_date]
                if day_data.empty:
                    continue
                current_price = day_data['Close'].iloc[0]
                reason, exit_price = self.check_exit(pos, current_date, current_price)
                if reason:
                    to_exit.append((pos, current_date, exit_price, reason))
            
            for pos, date, price, reason in to_exit:
                self.exit_position(pos, date, price, reason)
                self.portfolio.remove(pos)
            
            # Portfolio value tracking
            portfolio_value = self.calculate_portfolio_value(current_date, stock_data)
            self.daily_values.append({
                'Date': current_date,
                'Portfolio_Value': portfolio_value,
                'Positions': len(self.portfolio)
            })
            
            # Look for entries (weekly)
            if current_date.weekday() == 0 and len(self.portfolio) < self.max_portfolio:
                for symbol in stock_data.keys():
                    if len(self.portfolio) >= self.max_portfolio:
                        break
                    if any(p['symbol'] == symbol for p in self.portfolio):
                        continue
                    
                    df = stock_data[symbol]
                    historical = df[df['Date'] <= current_date]
                    if len(historical) < 50:
                        continue
                    
                    try:
                        # TRY AI FIRST (Hybrid approach)
                        buy_signal, confidence, reason = self.try_ai_signal(symbol, historical.tail(500))
                        source = 'AI'
                        
                        # FALLBACK TO TECHNICAL if AI fails
                        if not buy_signal:
                            buy_signal, confidence, reason = self.calculate_technical_signal(historical.tail(200))
                            source = 'Technical'
                        
                        if buy_signal:
                            entry_price = historical['Close'].iloc[-1]
                            self.enter_position(symbol, current_date, entry_price, reason, confidence, source)
                            self.signal_stats[source] += 1
                    except Exception as e:
                        # Skip this stock if signal generation fails
                        continue
        
        # Close remaining
        for pos in self.portfolio[:]:
            final_price = stock_data[pos['symbol']]['Close'].iloc[-1]
            self.exit_position(pos, end_date, final_price, 'BACKTEST_END')
            self.portfolio.remove(pos)
        
        return self.trades, self.daily_values, self.signal_stats


def load_stock_data(symbols, start_date, end_date):
    stock_data = {}
    data_dir = Path(__file__).parent / "data_till_feb2025"
    
    for symbol in symbols:
        data_file = data_dir / f"NSE_{symbol}_1D.csv"
        if not data_file.exists():
            continue
        
        df = pd.read_csv(data_file, parse_dates=['time'])
        df = df.rename(columns={'time': 'Date', 'open': 'Open', 'high': 'High',
                                'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        if len(df) >= 50:
            stock_data[symbol] = df
    
    return stock_data


def main():
    st.set_page_config(page_title="Hybrid Backtest Dashboard", layout="wide")
    
    st.title("📊 Hybrid Backtest Dashboard (AI + Technical)")
    st.caption("🤖 Uses AI models first, falls back to Technical Analysis")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("📈 Stock Selection")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Top 5", use_container_width=True):
                st.session_state['selected_stocks'] = NIFTY200_STOCKS[:5]
        with col2:
            if st.button("Top 10", use_container_width=True):
                st.session_state['selected_stocks'] = NIFTY200_STOCKS[:10]
        with col3:
            if st.button("Top 20", use_container_width=True):
                st.session_state['selected_stocks'] = NIFTY200_STOCKS[:20]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Nifty 50", use_container_width=True):
                st.session_state['selected_stocks'] = NIFTY200_STOCKS[:50]
        with col2:
            if st.button("All 169", use_container_width=True):
                st.session_state['selected_stocks'] = NIFTY200_STOCKS
        
        selected_stocks = st.multiselect(
            "Select Stocks",
            options=NIFTY200_STOCKS,
            default=st.session_state.get('selected_stocks', NIFTY200_STOCKS[:5]),
            help="AI + Technical Hybrid Strategy"
        )
        st.session_state['selected_stocks'] = selected_stocks
        st.caption(f"📊 Selected: {len(selected_stocks)} stocks")
        
        st.markdown("---")
        
        st.subheader("📅 Time Period")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime(2022, 3, 1))
        with col2:
            end_date = st.date_input("End Date", value=datetime(2025, 2, 28))
        
        st.markdown("---")
        
        st.subheader("🤖 AI Settings")
        ai_threshold = st.slider(
            "AI Confidence Threshold (%)",
            min_value=50,
            max_value=80,
            value=60,
            help="Minimum confidence required from AI model"
        )
        
        st.markdown("---")
        
        st.subheader("💼 Portfolio Settings")
        investment = st.number_input("Investment per Stock (Rs)", value=200000, step=50000)
        max_portfolio = st.number_input("Max Portfolio Size", value=20, min_value=1, max_value=50)
        
        st.markdown("---")
        
        st.subheader("🎯 Risk Management")
        target = st.slider("Target Return (%)", 5, 30, 10) / 100
        stop_loss = st.slider("Stop Loss (%)", 3, 15, 7) / 100
        max_holding = st.number_input("Max Holding Days", value=60, min_value=10, max_value=365)
        
        st.markdown("---")
        run_backtest = st.button("🚀 Run Hybrid Backtest", type="primary", use_container_width=True)
    
    # Main area
    if run_backtest:
        if not selected_stocks:
            st.error("❌ Please select at least one stock!")
            return
        
        with st.spinner("Running HYBRID backtest (AI + Technical)..."):
            start_ts = pd.Timestamp(start_date, tz='Asia/Kolkata')
            end_ts = pd.Timestamp(end_date, tz='Asia/Kolkata')
            
            stock_data = load_stock_data(selected_stocks, start_ts, end_ts)
            
            if not stock_data:
                st.error("❌ No data available!")
                return
            
            engine = HybridBacktestEngine(investment, max_portfolio, target, stop_loss, max_holding, ai_threshold)
            trades, daily_values, signal_stats = engine.run_backtest(stock_data, start_ts, end_ts)
            
            if not trades:
                st.warning("⚠️ No trades executed!")
                return
            
            df_trades = pd.DataFrame(trades)
            df_daily = pd.DataFrame(daily_values)
            
            # Statistics
            total_trades = len(df_trades)
            winners = len(df_trades[df_trades['PnL'] > 0])
            losers = len(df_trades[df_trades['PnL'] < 0])
            win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
            
            total_pnl = df_trades['PnL'].sum()
            avg_return = df_trades['Return_%'].mean()
            avg_holding = df_trades['Holding_Days'].mean()
            
            initial_capital = investment * max_portfolio
            total_return_pct = (total_pnl / initial_capital) * 100
            
            # Calculate annualized return
            days_in_backtest = (end_ts - start_ts).days
            years_in_backtest = days_in_backtest / 365.25
            
            # CAGR (Compound Annual Growth Rate)
            final_capital = initial_capital + total_pnl
            if years_in_backtest > 0 and final_capital > 0 and initial_capital > 0:
                cagr = (((final_capital / initial_capital) ** (1 / years_in_backtest)) - 1) * 100
            else:
                cagr = 0
            
            # Simple annualized return
            annualized_return = total_return_pct / years_in_backtest if years_in_backtest > 0 else 0
            
            # AI vs Technical breakdown
            ai_trades = len(df_trades[df_trades['Signal_Source'] == 'AI'])
            tech_trades = len(df_trades[df_trades['Signal_Source'] == 'Technical'])
            
            ai_pnl = df_trades[df_trades['Signal_Source'] == 'AI']['PnL'].sum() if ai_trades > 0 else 0
            tech_pnl = df_trades[df_trades['Signal_Source'] == 'Technical']['PnL'].sum() if tech_trades > 0 else 0
            
            st.success("✅ Hybrid Backtest Complete!")
            
            # Signal source breakdown
            st.header("🤖 Signal Source Analysis")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("AI Signals", ai_trades, f"{(ai_trades/total_trades*100):.1f}%")
            with col2:
                st.metric("Technical Signals", tech_trades, f"{(tech_trades/total_trades*100):.1f}%")
            with col3:
                st.metric("AI P&L", f"Rs{ai_pnl:,.0f}")
            with col4:
                st.metric("Technical P&L", f"Rs{tech_pnl:,.0f}")
            
            st.markdown("---")
            
            # Performance metrics
            st.header("📊 Performance Summary")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("Total P&L", f"Rs{total_pnl:,.0f}", f"{total_return_pct:.2f}%")
            with col2:
                st.metric("Annualized Return", f"{annualized_return:.2f}%", help="Average yearly portfolio return")
            with col3:
                st.metric("Total Trades", total_trades)
            with col4:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col5:
                st.metric("Avg Return/Trade", f"{avg_return:.2f}%")
            with col6:
                st.metric("Avg Holding", f"{avg_holding:.0f} days")
            
            st.markdown("---")
            
            # Portfolio chart
            st.header("📈 Portfolio Performance")
            if len(df_daily) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_daily['Date'],
                    y=df_daily['Portfolio_Value'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#2E86DE', width=2),
                    fill='tozeroy'
                ))
                fig.add_hline(y=initial_capital, line_dash="dash", line_color="gray",
                             annotation_text=f"Initial: Rs{initial_capital:,.0f}")
                fig.update_layout(title="Portfolio Value Over Time", xaxis_title="Date",
                                 yaxis_title="Value (Rs)", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio statistics
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("💰 Portfolio Performance")
                final_value = initial_capital + total_pnl
                st.write(f"**Initial Capital:** Rs{initial_capital:,.0f}")
                st.write(f"**Final Value:** Rs{final_value:,.0f}")
                st.write(f"**Total Portfolio Return:** {total_return_pct:.2f}%")
                st.write(f"**Annualized Return:** {annualized_return:.2f}% per year")
                st.write(f"**CAGR:** {cagr:.2f}%")
                st.write(f"**Total P&L:** Rs{total_pnl:,.0f}")
                st.write(f"**Period:** {years_in_backtest:.1f} years ({days_in_backtest} days)")
            
            with col2:
                st.subheader("📊 Trade Statistics")
                st.write(f"**Winners:** {ai_trades + tech_trades if ai_trades > 0 or tech_trades > 0 else winners} ({win_rate:.1f}%)")
                st.write(f"**Losers:** {losers}")
                avg_win = df_trades[df_trades['PnL'] > 0]['Return_%'].mean() if winners > 0 else 0
                avg_loss = df_trades[df_trades['PnL'] < 0]['Return_%'].mean() if losers > 0 else 0
                st.write(f"**Avg Win:** {avg_win:.2f}%")
                st.write(f"**Avg Loss:** {avg_loss:.2f}%")
            
            st.markdown("---")
            
            # Best and worst trades
            best_trade = df_trades.loc[df_trades['PnL'].idxmax()]
            worst_trade = df_trades.loc[df_trades['PnL'].idxmin()]
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏆 Best Trade")
                best_entry = best_trade['Entry_Date'].strftime('%Y-%m-%d') if hasattr(best_trade['Entry_Date'], 'strftime') else str(best_trade['Entry_Date'])
                best_exit = best_trade['Exit_Date'].strftime('%Y-%m-%d') if hasattr(best_trade['Exit_Date'], 'strftime') else str(best_trade['Exit_Date'])
                st.success(f"""
                **{best_trade['Symbol']}** ({best_trade['Signal_Source']})  
                Entry: {best_entry} @ Rs{best_trade['Entry_Price']:.2f}  
                Exit: {best_exit} @ Rs{best_trade['Exit_Price']:.2f}  
                **Return: {best_trade['Return_%']:.2f}%** (Rs{best_trade['PnL']:,.0f})
                """)
            
            with col2:
                st.subheader("📉 Worst Trade")
                worst_entry = worst_trade['Entry_Date'].strftime('%Y-%m-%d') if hasattr(worst_trade['Entry_Date'], 'strftime') else str(worst_trade['Entry_Date'])
                worst_exit = worst_trade['Exit_Date'].strftime('%Y-%m-%d') if hasattr(worst_trade['Exit_Date'], 'strftime') else str(worst_trade['Exit_Date'])
                st.error(f"""
                **{worst_trade['Symbol']}** ({worst_trade['Signal_Source']})  
                Entry: {worst_entry} @ Rs{worst_trade['Entry_Price']:.2f}  
                Exit: {worst_exit} @ Rs{worst_trade['Exit_Price']:.2f}  
                **Return: {worst_trade['Return_%']:.2f}%** (Rs{worst_trade['PnL']:,.0f})
                """)
            
            st.markdown("---")
            
            # Detailed trades table
            st.header("📋 All Trades (Showing Signal Source)")
            df_display = df_trades.copy()
            
            # Format dates (already datetime objects with timezone)
            df_display['Entry_Date'] = df_display['Entry_Date'].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x))
            df_display['Exit_Date'] = df_display['Exit_Date'].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x))
            
            # Format prices and values
            df_display['Entry_Price'] = df_display['Entry_Price'].apply(lambda x: f"Rs{x:.2f}")
            df_display['Exit_Price'] = df_display['Exit_Price'].apply(lambda x: f"Rs{x:.2f}")
            df_display['PnL'] = df_display['PnL'].apply(lambda x: f"Rs{x:,.0f}")
            df_display['Return_%'] = df_display['Return_%'].apply(lambda x: f"{x:.2f}%")
            df_display['Confidence'] = df_display['Confidence'].apply(lambda x: f"{x:.0f}%")
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Download
            csv = df_trades.to_csv(index=False)
            st.download_button(
                "📥 Download Results (CSV)",
                csv,
                f"hybrid_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    else:
        st.info("👈 Configure settings and click 'Run Hybrid Backtest'")
        st.markdown("""
        ### 🤖 Hybrid Strategy (AI + Technical):
        
        **How it works:**
        1. **Try AI Model First** - Uses XGBoost + LightGBM ensemble
        2. **Check Confidence** - If AI confidence ≥ threshold (default 60%)
        3. **Generate AI Signal** - If confident enough
        4. **Fallback to Technical** - If AI confidence too low
        5. **Track Signal Source** - Shows which system generated each signal
        
        **Advantages:**
        - ✅ Best of both worlds (AI intelligence + Technical reliability)
        - ✅ More trading opportunities
        - ✅ Transparency (know signal source for each trade)
        - ✅ Compare AI vs Technical performance
        
        **Quick Start:** Select Top 5, keep defaults, click Run!
        """)


if __name__ == "__main__":
    main()

