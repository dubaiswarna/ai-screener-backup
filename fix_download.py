#!/usr/bin/env python3
"""Fix 3Jasmines download button"""

import re

# Read the file
with open('enhanced_screener.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the old code
old_pattern = r'(                # Export option\n                st\.markdown\("---"\)\n)                if st\.button\("📥 Download 3Jasmines Signals \(CSV\)"\):\n                    df_export = pd\.DataFrame\(jasmines_signals\)\n                    csv = df_export\.to_csv\(index=False\)\n                    st\.download_button\(\n                        "Download CSV",\n                        csv,\n                        f"3jasmines_signals_\{pd\.Timestamp\.now\(\)\.strftime\('\%Y\%m\%d_\%H\%M\%S'\)\}\.csv",\n                        "text/csv"\n                    )'

# New code
new_code = '''                # Export option
                st.markdown("---")
                st.subheader("📥 Download 3Jasmines Signals")
                
                # Flatten nested dictionaries for CSV export
                try:
                    if not jasmines_signals or len(jasmines_signals) == 0:
                        st.warning("⚠️ No signals to export")
                    else:
                        # Create a flattened version for export
                        export_data = []
                        for signal in jasmines_signals:
                            # Safely extract nested data
                            j1 = signal.get('jasmine1_support', {}) if isinstance(signal.get('jasmine1_support'), dict) else {}
                            j2 = signal.get('jasmine2_rsi', {}) if isinstance(signal.get('jasmine2_rsi'), dict) else {}
                            j3 = signal.get('jasmine3_pattern', {}) if isinstance(signal.get('jasmine3_pattern'), dict) else {}
                            
                            flat_signal = {
                                'Symbol': str(signal.get('symbol', '')),
                                'Current_Price': float(signal.get('current_price', 0)),
                                'Entry': float(signal.get('entry', 0)),
                                'Stop_Loss': float(signal.get('stop_loss', 0)),
                                'Target': float(signal.get('target', 0)),
                                'Support_Level': float(signal.get('support_level', 0)),
                                'Resistance_Level': float(signal.get('resistance_level', 0)),
                                'Risk': float(signal.get('risk', 0)),
                                'Reward': float(signal.get('reward', 0)),
                                'RR_Ratio': float(signal.get('rr_ratio', 0)),
                                'Position_Size': int(signal.get('position_size', 0)),
                                'Potential_Profit': float(signal.get('potential_profit', 0)),
                                'Confidence': float(signal.get('confidence', 0)),
                                'Jasmine1_Score': float(j1.get('score', 0)),
                                'Jasmine1_Reason': str(j1.get('reason', '')),
                                'Jasmine2_RSI': float(j2.get('rsi_value', 0)),
                                'Jasmine2_Score': float(j2.get('score', 0)),
                                'Jasmine2_Reason': str(j2.get('reason', '')),
                                'Jasmine3_Pattern': str(j3.get('pattern_name', '')),
                                'Jasmine3_Score': float(j3.get('score', 0)),
                                'Jasmine3_Reason': str(j3.get('reason', '')),
                                'Strategy': str(signal.get('strategy', '')),
                                'Holding_Period': str(signal.get('holding_period', ''))
                            }
                            export_data.append(flat_signal)
                        
                        if export_data:
                            df_export = pd.DataFrame(export_data)
                            csv = df_export.to_csv(index=False)
                            
                            if csv and len(csv) > 0:
                                st.download_button(
                                    "📥 Download 3Jasmines Signals (CSV)",
                                    csv,
                                    f"3jasmines_signals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    "text/csv",
                                    key="download_jasmines_csv",
                                    type="primary",
                                    use_container_width=True,
                                    help="Click to download all 3Jasmines signals as CSV file"
                                )
                            else:
                                st.error("❌ Failed to generate CSV data")
                        else:
                            st.warning("⚠️ No data to export")
                except Exception as e:
                    st.error(f"❌ Error preparing download: {e}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())'''

# Simple search and replace
old_code = '''                if st.button("📥 Download 3Jasmines Signals (CSV)"):
                    df_export = pd.DataFrame(jasmines_signals)
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"3jasmines_signals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )'''

if old_code in content:
    content = content.replace(old_code, new_code.split('\n                # Export option\n                st.markdown("---")\n', 1)[-1])
    with open('enhanced_screener.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ FIXED: Replaced old nested button code with new direct download button")
else:
    print("❌ OLD CODE NOT FOUND - May already be fixed or pattern doesn't match")
    # Check if new code exists
    if 'st.subheader("📥 Download 3Jasmines Signals")' in content:
        print("✅ NEW CODE ALREADY EXISTS")
    else:
        print("⚠️ UNKNOWN STATE - Manual review needed")

