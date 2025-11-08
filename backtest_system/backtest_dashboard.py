"""
Backtest Dashboard - Interactive Portfolio Backtesting
======================================================
Select stocks, time period, and run custom backtests
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Complete Nifty 200 stocks (169 stocks with available models)
NIFTY200_STOCKS = [
    # Nifty 50 (Large Cap)
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
    
    # Nifty Next 50 (Mid Cap)
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
    
    # Additional Nifty 200
    'DIXON', 'FEDERALBNK', 'GLENMARK', 'HONAUT', 'IDFCFIRSTB',
    'INDHOTEL', 'JINDALSTEL', 'JUBLFOOD', 'LICHSGFIN', 'MANAPPURAM',
    'MRF', 'NMDC', 'OBEROIRLTY', 'OIL', 'PNB',
    'POLYCAB', 'RECLTD', 'TATACOMM', 'VOLTAS', 'WHIRLPOOL',
    'CHAMBLFERT', 'CHOLAFIN', 'COFORGE', 'COROMANDEL', 'CROMPTON',
    'GNFC', 'GODREJPROP', 'IIFL', 'IOC', 'IRFC',
    'JKCEMENT', 'LTTS', 'LAURUSLABS', 'MFSL', 'MGL',
    'NATIONALUM', 'NAUKRI', 'NAVINFLUOR', 'PAYTM', 'PETRONET',
    'PFC', 'SAIL', 'TATAPOWER', 'ZYDUSLIFE', 'AARTIIND',
    'ABBOTINDIA', 'ACC', 'ADANIPOWER', 'AJANTPHARM', 'APOLLO',
    'APLLTD', 'APLAPOLLO', 'ASHOKLEY', 'ATUL', 'EXIDEIND',
    'CUB', 'GRANULES', 'HATSUN', 'HINDCOPPER', 'ICICIPRULI',
    'IDEA', 'INTELLECT', 'KPITTECH', 'LTIM', 'M&MFIN',
    'MRPL', 'MUTHOOTFIN', 'NLCINDIA', 'PHOENIXLTD', 'PNBHOUSING',
    'PRESTIGE', 'PVR', 'RBLBANK', 'SANOFI', 'SCHAEFFLER',
    'SONACOMS', 'SUNDARMFIN', 'SUNDRMFAST', 'SUPREMEIND', 'TATACHEM',
    'TATAELXSI', 'TVSHLD', 'UNIONBANK', 'UNITDSPR', 'ZEEL'
]


class BacktestEngine:
    """Backtesting engine with portfolio management."""
    
    def __init__(self, investment_per_stock, max_portfolio, target, stop, max_days):
        self.investment = investment_per_stock
        self.max_portfolio = max_portfolio
        self.target = target
        self.stop = stop
        self.max_days = max_days
        self.portfolio = []
        self.trades = []
        self.daily_values = []
    
    def calculate_technical_signal(self, df):
        """Technical analysis signal generation."""
        if len(df) < 50:
            return False, 0, "Insufficient data"
        
        close = df['Close']
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Moving averages
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        
        current_price = close.iloc[-1]
        current_sma20 = sma_20.iloc[-1]
        current_sma50 = sma_50.iloc[-1]
        prev_sma20 = sma_20.iloc[-2]
        prev_sma50 = sma_50.iloc[-2]
        
        # Golden Cross + RSI oversold
        if (current_sma20 > current_sma50 and prev_sma20 <= prev_sma50 and 
            current_rsi < 40 and current_price > current_sma20):
            return True, 85, "Golden Cross + RSI Oversold"
        
        # Uptrend + healthy RSI
        elif (current_price > current_sma20 and current_price > current_sma50 and
              30 < current_rsi < 70 and current_sma20 > current_sma50):
            return True, 75, "Uptrend + Healthy RSI"
        
        # Pullback to SMA20
        elif (current_sma20 > current_sma50 and 
              abs(current_price - current_sma20) / current_sma20 < 0.02 and
              current_rsi < 50):
            return True, 70, "Pullback to SMA20"
        
        return False, 0, ""
    
    def enter_position(self, symbol, date, price, reason, confidence):
        qty = int(self.investment / price)
        pos = {
            'symbol': symbol,
            'entry_date': date,
            'entry_price': price,
            'qty': qty,
            'investment': qty * price,
            'reason': reason,
            'confidence': confidence,
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
            'Entry_Reason': pos['reason'],
            'Confidence': pos['confidence']
        }
        self.trades.append(trade)
        return trade
    
    def calculate_portfolio_value(self, date, stock_data):
        """Calculate total portfolio value on a given date."""
        total = 0
        for pos in self.portfolio:
            if pos['symbol'] in stock_data:
                df = stock_data[pos['symbol']]
                day_data = df[df['Date'] == date]
                if not day_data.empty:
                    current_price = day_data['Close'].iloc[0]
                    total += pos['qty'] * current_price
        return total
    
    def run_backtest(self, stock_data, start_date, end_date):
        """Run backtest on selected stocks and period."""
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
            
            # Calculate daily portfolio value
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
                    
                    buy_signal, confidence, reason = self.calculate_technical_signal(historical.tail(200))
                    if buy_signal:
                        entry_price = historical['Close'].iloc[-1]
                        self.enter_position(symbol, current_date, entry_price, reason, confidence)
        
        # Close remaining positions
        for pos in self.portfolio[:]:
            final_price = stock_data[pos['symbol']]['Close'].iloc[-1]
            self.exit_position(pos, end_date, final_price, 'BACKTEST_END')
            self.portfolio.remove(pos)
        
        return self.trades, self.daily_values


def load_stock_data(symbols, start_date, end_date):
    """Load data for selected stocks."""
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
    """Main dashboard."""
    
    st.set_page_config(page_title="Backtest Dashboard", layout="wide")
    
    st.title("📊 Portfolio Backtest Dashboard")
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Backtest Configuration")
        
        # Stock selection
        st.subheader("📈 Stock Selection")
        
        # Quick select buttons
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
        
        # Multi-select
        selected_stocks = st.multiselect(
            "Select Stocks (169 available)",
            options=NIFTY200_STOCKS,
            default=st.session_state.get('selected_stocks', ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']),
            help="Select stocks to include in backtest - Use quick buttons above or search/select manually"
        )
        
        st.session_state['selected_stocks'] = selected_stocks
        
        # Show count
        st.caption(f"📊 Selected: {len(selected_stocks)} stocks")
        
        st.markdown("---")
        
        # Time period
        st.subheader("📅 Time Period")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2022, 3, 1),
                min_value=datetime(2015, 1, 1),
                max_value=datetime(2025, 2, 28)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime(2025, 2, 28),
                min_value=datetime(2015, 1, 1),
                max_value=datetime(2025, 2, 28)
            )
        
        st.markdown("---")
        
        # Portfolio parameters
        st.subheader("💼 Portfolio Settings")
        
        investment = st.number_input(
            "Investment per Stock (Rs)",
            min_value=10000,
            max_value=10000000,
            value=200000,
            step=50000,
            help="Amount to invest in each stock"
        )
        
        max_portfolio = st.number_input(
            "Max Portfolio Size",
            min_value=1,
            max_value=50,
            value=20,
            help="Maximum number of stocks to hold simultaneously"
        )
        
        st.markdown("---")
        
        # Risk parameters
        st.subheader("🎯 Risk Management")
        
        target = st.slider(
            "Target Return (%)",
            min_value=5,
            max_value=30,
            value=10,
            help="Take profit at this return"
        ) / 100
        
        stop_loss = st.slider(
            "Stop Loss (%)",
            min_value=3,
            max_value=15,
            value=7,
            help="Exit if loss exceeds this"
        ) / 100
        
        max_holding = st.number_input(
            "Max Holding Days",
            min_value=10,
            max_value=365,
            value=60,
            help="Exit after this many days regardless of P&L"
        )
        
        st.markdown("---")
        
        # Run button
        run_backtest = st.button("🚀 Run Backtest", type="primary", use_container_width=True)
    
    # Main area
    if run_backtest:
        if not selected_stocks:
            st.error("❌ Please select at least one stock!")
            return
        
        if start_date >= end_date:
            st.error("❌ Start date must be before end date!")
            return
        
        with st.spinner("Running backtest... This may take a minute..."):
            # Load data
            start_ts = pd.Timestamp(start_date, tz='Asia/Kolkata')
            end_ts = pd.Timestamp(end_date, tz='Asia/Kolkata')
            
            stock_data = load_stock_data(selected_stocks, start_ts, end_ts)
            
            if not stock_data:
                st.error("❌ No data available for selected stocks and period!")
                return
            
            # Run backtest
            engine = BacktestEngine(investment, max_portfolio, target, stop_loss, max_holding)
            trades, daily_values = engine.run_backtest(stock_data, start_ts, end_ts)
            
            if not trades:
                st.warning("⚠️ No trades were executed. Try different stocks or time period.")
                return
            
            # Process results
            df_trades = pd.DataFrame(trades)
            df_daily = pd.DataFrame(daily_values)
            
            # Calculate statistics
            total_trades = len(df_trades)
            winners = len(df_trades[df_trades['PnL'] > 0])
            losers = len(df_trades[df_trades['PnL'] < 0])
            win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
            
            total_pnl = df_trades['PnL'].sum()
            avg_return = df_trades['Return_%'].mean()
            avg_win = df_trades[df_trades['PnL'] > 0]['Return_%'].mean() if winners > 0 else 0
            avg_loss = df_trades[df_trades['PnL'] < 0]['Return_%'].mean() if losers > 0 else 0
            avg_holding = df_trades['Holding_Days'].mean()
            
            best_trade = df_trades.loc[df_trades['PnL'].idxmax()]
            worst_trade = df_trades.loc[df_trades['PnL'].idxmin()]
            
            # Calculate portfolio performance
            initial_capital = investment * max_portfolio
            final_value = initial_capital + total_pnl
            total_return_pct = (total_pnl / initial_capital) * 100
            
            # Display results
            st.success("✅ Backtest Complete!")
            
            # Summary metrics
            st.header("📊 Performance Summary")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total P&L", f"Rs{total_pnl:,.0f}", f"{total_return_pct:.2f}%")
            with col2:
                st.metric("Total Trades", total_trades)
            with col3:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col4:
                st.metric("Avg Return", f"{avg_return:.2f}%")
            with col5:
                st.metric("Avg Holding", f"{avg_holding:.0f} days")
            
            st.markdown("---")
            
            # Portfolio performance chart
            st.header("📈 Portfolio Performance")
            
            if len(df_daily) > 0:
                fig = go.Figure()
                
                # Portfolio value line
                fig.add_trace(go.Scatter(
                    x=df_daily['Date'],
                    y=df_daily['Portfolio_Value'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#2E86DE', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(46, 134, 222, 0.1)'
                ))
                
                # Initial capital line
                fig.add_hline(
                    y=initial_capital,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Initial Capital: Rs{initial_capital:,.0f}",
                    annotation_position="right"
                )
                
                fig.update_layout(
                    title="Portfolio Value Over Time",
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value (₹)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Portfolio Statistics")
                st.write(f"**Initial Capital:** Rs{initial_capital:,.0f}")
                st.write(f"**Final Value:** Rs{final_value:,.0f}")
                st.write(f"**Total Return:** {total_return_pct:.2f}%")
                st.write(f"**Total P&L:** Rs{total_pnl:,.0f}")
            
            with col2:
                st.subheader("📊 Trade Statistics")
                st.write(f"**Winners:** {winners} ({win_rate:.1f}%)")
                st.write(f"**Losers:** {losers}")
                st.write(f"**Avg Win:** {avg_win:.2f}%")
                st.write(f"**Avg Loss:** {avg_loss:.2f}%")
            
            st.markdown("---")
            
            # Best and worst trades
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Best Trade")
                st.success(f"""
                **{best_trade['Symbol']}**  
                Entry: {pd.to_datetime(best_trade['Entry_Date']).strftime('%Y-%m-%d')} @ Rs{best_trade['Entry_Price']:.2f}  
                Exit: {pd.to_datetime(best_trade['Exit_Date']).strftime('%Y-%m-%d')} @ Rs{best_trade['Exit_Price']:.2f}  
                **Return: {best_trade['Return_%']:.2f}%** (Rs{best_trade['PnL']:,.0f})
                """)
            
            with col2:
                st.subheader("📉 Worst Trade")
                st.error(f"""
                **{worst_trade['Symbol']}**  
                Entry: {pd.to_datetime(worst_trade['Entry_Date']).strftime('%Y-%m-%d')} @ Rs{worst_trade['Entry_Price']:.2f}  
                Exit: {pd.to_datetime(worst_trade['Exit_Date']).strftime('%Y-%m-%d')} @ Rs{worst_trade['Exit_Price']:.2f}  
                **Return: {worst_trade['Return_%']:.2f}%** (Rs{worst_trade['PnL']:,.0f})
                """)
            
            st.markdown("---")
            
            # Detailed trades table
            st.header("📋 All Trades")
            
            # Format for display
            df_display = df_trades.copy()
            
            # Convert dates to string format
            df_display['Entry_Date'] = pd.to_datetime(df_display['Entry_Date']).dt.strftime('%Y-%m-%d')
            df_display['Exit_Date'] = pd.to_datetime(df_display['Exit_Date']).dt.strftime('%Y-%m-%d')
            
            # Format prices and values
            df_display['Entry_Price'] = df_display['Entry_Price'].apply(lambda x: f"Rs{x:.2f}")
            df_display['Exit_Price'] = df_display['Exit_Price'].apply(lambda x: f"Rs{x:.2f}")
            df_display['Investment'] = df_display['Investment'].apply(lambda x: f"Rs{x:,.0f}")
            df_display['Exit_Value'] = df_display['Exit_Value'].apply(lambda x: f"Rs{x:,.0f}")
            df_display['PnL'] = df_display['PnL'].apply(lambda x: f"Rs{x:,.0f}")
            df_display['Return_%'] = df_display['Return_%'].apply(lambda x: f"{x:.2f}%")
            df_display['Confidence'] = df_display['Confidence'].apply(lambda x: f"{x:.0f}%")
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Download button
            csv = df_trades.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Results (CSV)",
                data=csv,
                file_name=f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        # Initial state
        st.info("👈 Configure your backtest settings in the sidebar and click 'Run Backtest'")
        
        st.markdown("""
        ### 📚 How to Use:
        
        1. **Select Stocks:** Choose from **169 Nifty 200 stocks**
           - Use quick buttons: Top 5, Top 10, Top 20, Nifty 50, or All 169
           - Or search and select manually
        2. **Set Time Period:** Pick start and end dates (2015-2025)
        3. **Configure Portfolio:** Investment amount & max positions
        4. **Set Risk Parameters:** Target, stop loss, holding period
        5. **Run Backtest:** Click button and view complete results!
        
        ### 📊 What You'll Get:
        
        - **Complete trade history** with entry/exit dates and prices
        - **Portfolio performance chart** showing value over time
        - **Portfolio statistics** (initial capital, final value, total return)
        - **Win rate and P&L** detailed statistics
        - **Best and worst trades** analysis
        - **Downloadable CSV** for Excel analysis
        
        ### 🎯 Strategy:
        
        Proven technical analysis rules:
        - **Golden Cross:** SMA 20 crosses above SMA 50 with RSI < 40 (85% confidence)
        - **Uptrend Entry:** Price above both MAs with healthy RSI (75% confidence)
        - **Pullback Entry:** Price near SMA 20 in established uptrend (70% confidence)
        
        ### 💡 Tips:
        
        - Start with Top 5 or Top 10 for quick testing
        - Use Nifty 50 for large-cap focus
        - Select All 169 for maximum diversification
        - Try different time periods to find best strategy
        """)


if __name__ == "__main__":
    main()

