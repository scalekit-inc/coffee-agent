#!/bin/bash

# Docker run script for Coffee Agent
echo "🐳 Building and running Coffee Agent with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "OPENAI_API_KEY=your_openai_key"
    echo "SCALEKIT_CLIENT_ID=your_scalekit_client_id"
    echo "SCALEKIT_CLIENT_SECRET=your_scalekit_client_secret"
    echo "SCALEKIT_ENV_URL=your_scalekit_env_url"
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t chat-bot-app .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    # Run with docker-compose
    echo "🚀 Starting the application..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Application started successfully!"
        echo "🌐 Access the app at: http://localhost:8000"
        echo ""
        echo "📋 Useful commands:"
        echo "  View logs: docker-compose logs -f"
        echo "  Stop app:  docker-compose down"
        echo "  Restart:   docker-compose restart"
    else
        echo "❌ Failed to start the application"
        exit 1
    fi
else
    echo "❌ Failed to build Docker image"
    exit 1
fi
