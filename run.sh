#!/bin/bash

# IAM Policy Generator Startup Script

set -e

echo "Starting IAM Policy Generator..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo ".env file not found. Creating from template..."
    cp .env.example .env
    echo "Please edit .env file and add your OpenAI API key"
    echo "   OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "OpenAI API key not found in .env file"
    echo "Please edit .env file and add your OpenAI API key"
    echo "   OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Using Docker to run the application..."
    docker-compose up --build
elif command -v python3 &> /dev/null; then
    echo " Using Python to run the application..."
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo "Starting Flask application..."
    python app.py
else
    echo "Neither Docker nor Python3 found. Please install one of them."
    exit 1
fi
