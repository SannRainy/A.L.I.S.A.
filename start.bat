@echo off
echo Memulai Proyek Skripsi TVJP...
echo Sabar yaa...

:: FIX: Set UTF-8 encoding so Python/loguru can print Japanese characters without crashing
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
:: FIX: Model sudah ada di cache lokal, skip koneksi ke HuggingFace (stop retry spam)
:: (Komen dinonaktifkan karena kita butuh koneksi ke HF Cloud)
:: set TRANSFORMERS_OFFLINE=1
:: set HF_DATASETS_OFFLINE=1

npx --yes concurrently -k -n "Backend,Frontend,TTS" -c "cyan.bold,magenta.bold,yellow.bold" "call venv-backend\Scripts\activate.bat && cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000" "cd frontend && npm run dev" "call style-bert-vits2\venv-tts\Scripts\activate.bat && cd Style-Bert-VITS2 && python server_fastapi.py"
