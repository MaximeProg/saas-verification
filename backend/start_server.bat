@echo off
echo 🚀 Demarrage du serveur FastAPI KYC Platform...
echo.

call venv\Scripts\activate

echo ✅ Environnement virtuel active
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
