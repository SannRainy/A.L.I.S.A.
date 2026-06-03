@echo off
echo [A.L.I.S.A.] Installing TTS dependencies...
echo.

:: Install PyTorch dulu (skip jika sudah ada)
echo [1/3] Checking PyTorch (cu121)...
venv-tts\Scripts\python.exe -c "import torch; print('PyTorch already installed: ' + torch.__version__)" 2>nul || (
    echo Installing PyTorch...
    venv-tts\Scripts\python.exe -m pip install "torch==2.4.0" "torchaudio==2.4.0" --index-url https://download.pytorch.org/whl/cu121
)

:: Install dependencies TTS (sudah diperbaiki - tanpa av build error)
echo [2/3] Installing Style-Bert-VITS2 requirements...
venv-tts\Scripts\python.exe -m pip install -r Style-Bert-VITS2\requirements-tts.txt

:: Fix protobuf agar kompatibel dengan supabase & google packages
echo [3/3] Ensuring protobuf compatibility...
venv-tts\Scripts\python.exe -m pip install "protobuf>=5.26.1,<6.0.0" --quiet

echo.
echo [A.L.I.S.A.] TTS dependencies installed successfully!
