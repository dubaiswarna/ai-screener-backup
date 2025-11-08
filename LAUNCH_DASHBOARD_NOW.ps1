# Launch Dashboard Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   LAUNCHING AI SCREENER DASHBOARD" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\python\MG AI\AI_Screener_Complete"

Write-Host "Starting Streamlit server..." -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard will open at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Launch Streamlit
python -m streamlit run enhanced_screener.py --server.headless false

Write-Host ""
Write-Host "Dashboard stopped." -ForegroundColor Red

