#!/bin/bash
set -e

echo "🎓 Starting StudySmart AI..."

# Start backend
echo "📡 Starting FastAPI backend..."
cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "Installing backend dependencies..."
pip install -q -r requirements.txt

echo "Launching API server on http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
echo "🎨 Starting React frontend..."
cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Launching frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ StudySmart AI is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "⚠️  Set your GEMINI_API_KEY in backend/.env"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
