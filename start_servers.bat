@echo off
echo Iniciando servidores...

echo.
echo Ativando ambiente virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Ambiente virtual ativado.
) else (
    echo AVISO: Ambiente virtual nao encontrado em venv/
)

echo.
echo [1/2] Iniciando API backend (porta 5000)...
start "API Backend" cmd /k "cd backend\api && python app.py"

echo.
echo [2/2] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo Iniciando frontend (porta 3000)...
start "Frontend" cmd /k "cd frontend && python app.py"

echo.
echo Servidores iniciados!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar este terminal...
pause >nul