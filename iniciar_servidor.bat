@echo off
title Conciliador Modular

cd /d "C:\Users\yan.fernandes\Desktop\conciliador"

call ".venv\Scripts\activate.bat"

echo.
echo Iniciando Conciliador Modular...
echo Acesse neste computador: http://127.0.0.1:8000
echo Acesse na rede: http://192.168.1.214:8000
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause