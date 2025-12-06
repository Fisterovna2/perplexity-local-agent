#!/bin/bash
echo '🚀 Perplexity Local Agent Startup'
echo '================================'
echo ''
echo 'STEP 1: Installing dependencies...'
pip install -r backend/requirements.txt
echo '✅ Dependencies installed'
echo ''
echo 'STEP 2: Starting Backend (Flask)...'
echo 'Backend running on: http://localhost:5000'
echo ''
echo 'STEP 3: Open frontend/index.html in your browser'
echo 'Status should show: ✅ Online'
echo ''
echo 'Press Ctrl+C to stop'
echo '================================'
echo ''
cd backend
python agent.py
