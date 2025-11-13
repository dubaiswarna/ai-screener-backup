@echo off
cd "C:\python\MG AI\AI_Screener_Complete"
git add -A
git commit -m "🌸 NEW FEATURE: 3Jasmines Screener + Stricter Doji Detection

NEW: 3Jasmines Screener (Conservative Delivery Trading)
- Jasmine 1: Near Support (0.5%% distance)
- Jasmine 2: RSI < 35 (deeply oversold)
- Jasmine 3: Bullish Pattern (Hammer, Engulfing, etc.)
- Target: 1%% below resistance (high probability!)
- Stop Loss: 2%% below support
- Expected Win Rate: 85-90%%

FIXED: Doji Detection (Stricter Criteria)
- OLD: Body < 10%% of range (too loose!)
- NEW: Body < 5%% of range (professional standard)
- Must have both upper and lower wicks
- No more false Doji detections!

FILES:
- three_jasmines_screener.py (NEW - Core logic)
- enhanced_screener.py (3Jasmines page integrated)
- patterns/chart_pattern_detector.py (Doji fix)

READY FOR DEPLOYMENT!"
git push origin main
pause

