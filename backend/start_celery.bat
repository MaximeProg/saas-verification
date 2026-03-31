@echo off
echo 🔧 Demarrage Celery Worker...
echo.

call venv\Scripts\activate

echo ✅ Environnement virtuel active
echo.
echo ⚠️  Assurez-vous que Redis est lance (localhost:6379)
echo.

celery -A app.celery_app worker --loglevel=info --pool=solo -Q images,emails,webhooks,celery

pause
