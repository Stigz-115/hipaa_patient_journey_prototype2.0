#!/bin/bash
set -e

VITE_PORT=${APP_PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-3201}
export VITE_BACKEND_PORT=$BACKEND_PORT

echo "[*] Starting FastAPI backend on port $BACKEND_PORT..."
python3 -m uvicorn app:asgi --reload --host 0.0.0.0 --port $BACKEND_PORT \
  --reload-exclude "node_modules" &
BACKEND_PID=$!

echo "[*] Starting Vite frontend on port $VITE_PORT..."
VITE_BACKEND_PORT=$BACKEND_PORT npx vite --host 0.0.0.0 --port $VITE_PORT --strictPort

kill $BACKEND_PID 2>/dev/null
