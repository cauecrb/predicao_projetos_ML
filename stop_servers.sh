#!/bin/bash

echo "Parando servidores..."

if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill $BACKEND_PID 2>/dev/null
    rm .backend_pid
    echo "Backend parado (PID: $BACKEND_PID)"
fi

if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend_pid
    echo "Frontend parado (PID: $FRONTEND_PID)"
fi

echo "Pronto!"