@echo off
echo ============================================================
echo ADVANCED AI TRAINING - MAXIMUM ACCURACY MODE
echo ============================================================
echo.
echo This will train AI models with:
echo - Hyperparameter optimization (Grid Search)
echo - Cross-validation
echo - Advanced feature engineering
echo.
echo Expected time: 10-20 minutes total
echo Target accuracy: 95%+ for Gold, 90%+ for Silver
echo.
echo ============================================================

cd /d "%~dp0"

"..\venv\Scripts\python.exe" train_advanced_ai.py

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
pause

