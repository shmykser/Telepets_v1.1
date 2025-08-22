@echo off
echo Starting Telepets Backend...
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 3000 --reload
pause 