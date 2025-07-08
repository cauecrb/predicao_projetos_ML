#!/bin/bash

echo "Iniciando servidores..."

echo
echo "[1/2] Iniciando API backend (porta 5000)..."
cd backend/api
python3 app.py &
BACKEND_PID=$!
cd ../..

echo
echo "[2/2] Aguardando 3 segundos..."
sleep 3

echo "Iniciando frontend (porta 3000)..."
cd frontend
python3 app.py &
FRONTEND_PID=$!
cd ..

echo
echo "Servidores iniciados!"
echo "Backend: http://localhost:5000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo
echo "Para parar os servidores, execute: ./stop_servers.sh"

# Salvar PIDs para poder parar depois
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

wait