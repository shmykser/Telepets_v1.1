@echo off
echo Starting Telepets Backend...
REM Запуск как пакет для корректных относительных импортов
python -m uvicorn backend.main:app --host 127.0.0.1 --port 3000 --reload
pause 