#!/bin/bash

# Start the backend (FastAPI)
echo "Starting backend..."
python3 /backend/main.py &

# Start the frontend (React)
echo "Starting frontend..."
cd /frontend
npm start &

# Wait for background processes to complete
wait