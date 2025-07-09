#!/bin/bash

echo "Iniciando servidores..."

echo
echo "Ativando ambiente virtual..."
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
    echo "Ambiente virtual ativado."
else
    echo "AVISO: Ambiente virtual não encontrado em venv/"
fi

echo
echo "[1/2] Iniciando API backend (porta 5000)..."
cd backend/api
python3 app.py &
BACKEND_PID=$!
cd ../..

echo
echo "[2/2] Aguardando 3 segundos..."
sleep 3

echo "Iniciando web chatbot (porta 5001)..."
cd chat_bot/chatbot
python3 web_chatbot.py &
CHATBOT_PID=$!
cd ../..

echo
echo "Servidores iniciados!"
echo "Backend API: http://localhost:5000 (PID: $BACKEND_PID)"
echo "Web Chatbot: http://localhost:5001 (PID: $CHATBOT_PID)"
echo
echo "Para parar os servidores, execute: ./stop_servers.sh"

# Salvar PIDs para poder parar depois
echo $BACKEND_PID > .backend_pid
echo $CHATBOT_PID > .chatbot_pid

wait