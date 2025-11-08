@echo off
REM AI Stock Screener - Installation Script for Windows
echo ========================================
echo AI Stock Screener - Installation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Step 1: Installing core dependencies...
pip install pandas numpy scikit-learn pyyaml joblib openpyxl --quiet

echo Step 2: Installing XGBoost...
pip install xgboost --quiet

echo Step 3: Installing Streamlit...
pip install streamlit --quiet

echo Step 4: Installing Plotly...
pip install plotly --quiet

echo.
echo Step 5: Optional - Installing TensorFlow/Keras...
echo (This may take several minutes...)
pip install tensorflow --quiet

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: streamlit run screener_app.py
echo 2. Open browser at http://localhost:8501
echo 3. Train models: python train_models.py
echo.
pause

