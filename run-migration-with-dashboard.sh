#!/bin/bash
echo "🚀 Starting Vibekanban + Migration Swarm..."
PORT=3000 npx vibe-kanban > /dev/null 2>&1 &
VIBE_PID=$!
sleep 3
python main.py start "$1" --phase "${2:-1}"
kill $VIBE_PID 2>/dev/null
