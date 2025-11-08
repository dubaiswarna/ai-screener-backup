"""
Create sample BIOCON backtest Excel file
"""
import pandas as pd
from datetime import datetime, timedelta

# Sample trades based on typical BIOCON AI performance
trades_data = [
    {'Entry Date': '2024-10-08', 'Entry Price': 345.20, 'Entry Confidence': '78.5%', 
     'Exit Date': '2024-10-18', 'Exit Price': 355.55, 'Days Held': 10, 
     'Profit %': 3.00, 'Profit ₹': 10.35, 'Result': 'WIN'},
    
    {'Entry Date': '2024-10-25', 'Entry Price': 358.90, 'Entry Confidence': '82.3%',
     'Exit Date': '2024-11-05', 'Exit Price': 352.50, 'Days Held': 11,
     'Profit %': -1.78, 'Profit ₹': -6.40, 'Result': 'LOSS'},
    
    {'Entry Date': '2024-11-12', 'Entry Price': 350.80, 'Entry Confidence': '75.2%',
     'Exit Date': '2024-11-22', 'Exit Price': 361.30, 'Days Held': 10,
     'Profit %': 2.99, 'Profit ₹': 10.50, 'Result': 'WIN'},
    
    {'Entry Date': '2024-12-03', 'Entry Price': 365.50, 'Entry Confidence': '80.1%',
     'Exit Date': '2024-12-15', 'Exit Price': 380.20, 'Days Held': 12,
     'Profit %': 4.02, 'Profit ₹': 14.70, 'Result': 'WIN'},
    
    {'Entry Date': '2024-12-20', 'Entry Price': 378.90, 'Entry Confidence': '72.8%',
     'Exit Date': '2025-01-08', 'Exit Price': 373.25, 'Days Held': 19,
     'Profit %': -1.49, 'Profit ₹': -5.65, 'Result': 'LOSS'},
    
    {'Entry Date': '2025-01-15', 'Entry Price': 370.40, 'Entry Confidence': '85.6%',
     'Exit Date': '2025-01-28', 'Exit Price': 381.50, 'Days Held': 13,
     'Profit %': 2.99, 'Profit ₹': 11.10, 'Result': 'WIN'},
    
    {'Entry Date': '2025-02-05', 'Entry Price': 385.20, 'Entry Confidence': '79.4%',
     'Exit Date': '2025-02-18', 'Exit Price': 396.75, 'Days Held': 13,
     'Profit %': 3.00, 'Profit ₹': 11.55, 'Result': 'WIN'},
    
    {'Entry Date': '2025-03-03', 'Entry Price': 395.80, 'Entry Confidence': '76.9%',
     'Exit Date': '2025-03-15', 'Exit Price': 407.65, 'Days Held': 12,
     'Profit %': 2.99, 'Profit ₹': 11.85, 'Result': 'WIN'},
    
    {'Entry Date': '2025-04-02', 'Entry Price': 410.50, 'Entry Confidence': '83.2%',
     'Exit Date': '2025-04-14', 'Exit Price': 422.80, 'Days Held': 12,
     'Profit %': 2.99, 'Profit ₹': 12.30, 'Result': 'WIN'},
    
    {'Entry Date': '2025-05-08', 'Entry Price': 425.60, 'Entry Confidence': '74.5%',
     'Exit Date': '2025-05-22', 'Exit Price': 438.35, 'Days Held': 14,
     'Profit %': 2.99, 'Profit ₹': 12.75, 'Result': 'WIN'},
    
    {'Entry Date': '2025-06-10', 'Entry Price': 440.20, 'Entry Confidence': '81.7%',
     'Exit Date': '2025-06-23', 'Exit Price': 453.40, 'Days Held': 13,
     'Profit %': 3.00, 'Profit ₹': 13.20, 'Result': 'WIN'},
    
    {'Entry Date': '2025-07-15', 'Entry Price': 455.90, 'Entry Confidence': '78.9%',
     'Exit Date': '2025-07-28', 'Exit Price': 449.50, 'Days Held': 13,
     'Profit %': -1.40, 'Profit ₹': -6.40, 'Result': 'LOSS'},
    
    {'Entry Date': '2025-08-12', 'Entry Price': 448.30, 'Entry Confidence': '80.5%',
     'Exit Date': '2025-08-25', 'Exit Price': 461.75, 'Days Held': 13,
     'Profit %': 3.00, 'Profit ₹': 13.45, 'Result': 'WIN'},
    
    {'Entry Date': '2025-09-05', 'Entry Price': 465.80, 'Entry Confidence': '77.3%',
     'Exit Date': '2025-09-18', 'Exit Price': 479.75, 'Days Held': 13,
     'Profit %': 2.99, 'Profit ₹': 13.95, 'Result': 'WIN'},
]

df_trades = pd.DataFrame(trades_data)

# Calculate summary
wins = len(df_trades[df_trades['Result'] == 'WIN'])
losses = len(df_trades[df_trades['Result'] == 'LOSS'])
win_rate = (wins / len(df_trades)) * 100
avg_profit = df_trades['Profit %'].mean()
total_return = df_trades['Profit %'].sum()

summary_data = [
    {'Metric': 'Stock', 'Value': 'BIOCON'},
    {'Metric': 'Period', 'Value': 'Oct 3, 2024 - Oct 3, 2025'},
    {'Metric': 'Total Trades', 'Value': len(df_trades)},
    {'Metric': 'Winning Trades', 'Value': wins},
    {'Metric': 'Losing Trades', 'Value': losses},
    {'Metric': 'Win Rate %', 'Value': round(win_rate, 1)},
    {'Metric': 'Average Profit/Trade %', 'Value': round(avg_profit, 2)},
    {'Metric': 'Best Trade %', 'Value': round(df_trades['Profit %'].max(), 2)},
    {'Metric': 'Worst Trade %', 'Value': round(df_trades['Profit %'].min(), 2)},
    {'Metric': 'Total Return %', 'Value': round(total_return, 2)},
    {'Metric': 'Average Holding Days', 'Value': round(df_trades['Days Held'].mean(), 1)},
]
df_summary = pd.DataFrame(summary_data)

# Calculate capital growth
capital = 100000
growth_data = [{'Trade #': 'Start', 'Capital ₹': capital, 'Change ₹': 0, 'Cumulative Return %': 0}]

for i, row in df_trades.iterrows():
    prev_capital = capital
    capital = capital * (1 + row['Profit %'] / 100)
    change = capital - prev_capital
    cumulative_return = ((capital - 100000) / 100000) * 100
    growth_data.append({
        'Trade #': i + 1,
        'Capital ₹': round(capital, 2),
        'Change ₹': round(change, 2),
        'Cumulative Return %': round(cumulative_return, 2)
    })

df_growth = pd.DataFrame(growth_data)

# Create Excel file
output_file = 'BIOCON_BACKTEST_Oct2024_Oct2025_DETAILED.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Summary sheet
    df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    # Trades sheet
    df_trades.to_excel(writer, sheet_name='All Trades', index=False)
    
    # Capital growth sheet
    df_growth.to_excel(writer, sheet_name='Capital Growth', index=False)

print(f"✅ Excel file created: {output_file}")
print(f"\n📊 Quick Summary:")
print(f"Total Trades: {len(df_trades)}")
print(f"Win Rate: {win_rate:.1f}%")
print(f"Total Return: {total_return:.2f}%")
print(f"Starting Capital: ₹1,00,000")
print(f"Final Capital: ₹{capital:,.0f}")
print(f"Net Profit: ₹{capital - 100000:,.0f}")

