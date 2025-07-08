@echo off
echo Parando servidores...

taskkill /f /im python.exe 2>nul
echo Processos Python finalizados.

echo Pronto!
pause