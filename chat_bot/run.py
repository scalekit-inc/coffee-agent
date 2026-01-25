#!/usr/bin/env python3
"""
Simple startup script for local development
"""
from app import app

if __name__ == '__main__':
    print("🚀 Starting Coffee Agent...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🔑 Make sure you have set OPENAI_API_KEY in your .env file")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
