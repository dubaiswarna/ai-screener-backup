"""
Export Current NSE Signals to Detailed Excel Format
===================================================
Same format as BIOCON backtest - Entry/Exit details
"""

import pandas as pd
from datetime import datetime

# Current signals from the dashboard
signals_data = [
    {
        'Stock': 'NSE_BAJAJFINSV',
        'Signal': 'SELL',
        'Confidence': '98.5%',
        'Current Price': 2131.90,
        'Target Price': 2067.94,
        'Stop Loss': 2163.88,
        'VWAP': 2135.37,
        'VWAP Deviation': '-0.16%',
        'Recommendation': 'SHORT SELL'
    },
    {
        'Stock': 'NSE_BIOCON',
        'Signal': 'SELL',
        'Confidence': '97.2%',
        'Current Price': 375.30,
        'Target Price': 364.04,
        'Stop Loss': 380.93,
        'VWAP': 376.58,
        'VWAP Deviation': '-0.34%',
        'Recommendation': 'SHORT SELL'
    },
    {
        'Stock': 'NSE_CIPLA',
        'Signal': 'SELL',
        'Confidence': '96.8%',
        'Current Price': 1512.45,
        'Target Price': 1467.08,
        'Stop Loss': 1535.14,
        'VWAP': 1516.53,
        'VWAP Deviation': '-0.27%',
        'Recommendation': 'SHORT SELL'
    },
    {
        'Stock': 'NSE_DRREDDY',
        'Signal': 'SELL',
        'Confidence': '92.3%',
        'Current Price': 1268.75,
        'Target Price': 1230.69,
        'Stop Loss': 1287.78,
        'VWAP': 1271.42,
        'VWAP Deviation': '-0.21%',
        'Recommendation': 'SHORT SELL'
    },
    {
        'Stock': 'NSE_EICHERMOT',
        'Signal': 'SELL',
        'Confidence': '89.1%',
        'Current Price': 5180.25,
        'Target Price': 5024.84,
        'Stop Loss': 5257.95,
        'VWAP': 5189.17,
        'VWAP Deviation': '-0.17%',
        'Recommendation': 'SHORT SELL'
    },
    {
        'Stock': 'NSE_ETERNAL',
        'Signal': 'SELL',
        'Confidence': '87.5%',
        'Current Price': 2845.60,
        'Target Price': 2760.23,
        'Stop Loss': 2888.28,
        'VWAP': 2852.33,
        'VWAP Deviation': '-0.24%',
        'Recommendation': 'SHORT SELL'
    }
]

# Create main signals dataframe
df_signals = pd.DataFrame(signals_data)

# Create trading plan with entry/exit format
today = datetime.now()
trading_plan = []

for i, signal in enumerate(signals_data, 1):
    trading_plan.append({
        'Trade #': i,
        'Stock': signal['Stock'],
        'AI Signal': signal['Signal'],
        'Confidence': signal['Confidence'],
        'Entry Date': today.strftime('%Y-%m-%d'),
        'Entry Price': f"₹{signal['Current Price']:.2f}",
        'Target Price': f"₹{signal['Target Price']:.2f}",
        'Stop Loss': f"₹{signal['Stop Loss']:.2f}",
        'Expected Profit': f"{((signal['Current Price'] - signal['Target Price'])/signal['Current Price']*100):.2f}%",
        'Risk': f"{((signal['Stop Loss'] - signal['Current Price'])/signal['Current Price']*100):.2f}%",
        'Risk:Reward': '2:1',
        'Action': 'ENTER SHORT POSITION',
        'Exit Strategy': 'Target: 3% profit OR Stop: 1.5% loss',
        'Status': 'WAITING FOR ENTRY'
    })

df_trading_plan = pd.DataFrame(trading_plan)

# Summary statistics
summary = [
    {'Metric': 'Date Generated', 'Value': today.strftime('%Y-%m-%d %H:%M')},
    {'Metric': 'Total Signals', 'Value': 6},
    {'Metric': 'Buy Signals', 'Value': 0},
    {'Metric': 'Sell Signals', 'Value': 6},
    {'Metric': 'Average Confidence', 'Value': '93.8%'},
    {'Metric': 'Recommended Action', 'Value': 'SHORT SELL on all 6 stocks'},
    {'Metric': 'AI Model', 'Value': 'XGBoost (89 features)'},
    {'Metric': 'Market Status', 'Value': 'OPEN'},
]
df_summary = pd.DataFrame(summary)

# Risk analysis
risk_analysis = []
for signal in signals_data:
    capital_per_trade = 100000 / 6  # Assuming ₹1L divided across 6 trades
    shares = int(capital_per_trade / signal['Current Price'])
    max_loss = shares * (signal['Stop Loss'] - signal['Current Price'])
    expected_profit = shares * (signal['Current Price'] - signal['Target Price'])
    
    risk_analysis.append({
        'Stock': signal['Stock'],
        'Capital Allocated': f"₹{capital_per_trade:.0f}",
        'Shares to Short': shares,
        'Current Value': f"₹{shares * signal['Current Price']:.0f}",
        'Max Loss (if Stop hit)': f"₹{max_loss:.0f}",
        'Expected Profit (if Target hit)': f"₹{expected_profit:.0f}",
        'Risk %': '1.5%',
        'Reward %': '3.0%'
    })

df_risk = pd.DataFrame(risk_analysis)

# Create Excel file
output_file = 'NSE_AI_SIGNALS_DETAILED_' + today.strftime('%Y%m%d_%H%M') + '.xlsx'

with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    # Summary sheet
    df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    # Trading Plan sheet
    df_trading_plan.to_excel(writer, sheet_name='Trading Plan', index=False)
    
    # Current Signals sheet
    df_signals.to_excel(writer, sheet_name='Current Signals', index=False)
    
    # Risk Analysis sheet
    df_risk.to_excel(writer, sheet_name='Risk Analysis', index=False)
    
    # Get workbook and add formats
    workbook = writer.book
    
    # Format Summary sheet
    worksheet = writer.sheets['Summary']
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 30)
    
    # Format Trading Plan
    worksheet = writer.sheets['Trading Plan']
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:L', 15)
    
    # Format signals
    worksheet = writer.sheets['Current Signals']
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:J', 15)

print(f"✅ Excel file created: {output_file}")
print()
print("📊 Summary:")
print(f"   Total Signals: 6")
print(f"   All SELL signals (SHORT opportunities)")
print(f"   Average Confidence: 93.8%")
print()
print("📋 File contains 4 sheets:")
print("   1. Summary - Overview and statistics")
print("   2. Trading Plan - Entry/exit strategy for each stock")
print("   3. Current Signals - Raw AI predictions")
print("   4. Risk Analysis - Position sizing and risk calculation")
print()
print("💡 These are SHORT SELL signals - profit when price drops!")

