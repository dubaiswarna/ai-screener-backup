@echo off
echo ============================================================
echo WORLD-CLASS AI ENSEMBLE TRAINING SYSTEM
echo ============================================================
echo.
echo Training 9 AI Models per Commodity:
echo   1. XGBoost
echo   2. Random Forest
echo   3. Extra Trees
echo   4. AdaBoost
echo   5. Gradient Boosting
echo   6. LightGBM
echo   7. CatBoost
echo   8. Voting Ensemble
echo   9. Stacking Ensemble
echo.
echo This will take 5-10 minutes...
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" train_ensemble_models.py

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
echo.
pause

