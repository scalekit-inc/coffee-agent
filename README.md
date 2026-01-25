# ☕ Coffee Agent

A modern, coffee-themed AI chat application built with Flask and OpenAI, featuring integrations with Gmail, Google Calendar, and Notion through ScaleKit.

## 📁 Repository Structure

This repository contains:

- **`chat_bot/`** - Main Coffee Agent application
  - Flask-based web application
  - Gmail, Calendar, and Notion integrations via ScaleKit
  - Docker configuration for deployment
  - See [chat_bot/README.md](chat_bot/README.md) for detailed documentation

- **`scalekit_agent_connect/`** - ScaleKit integration examples
  - Reference implementations for different AI frameworks
  - Examples for LangChain, OpenAI, MCP, and direct usage

## 🚀 Quick Start

The main application is in the `chat_bot/` directory. To get started:

```bash
cd chat_bot
# Follow the setup instructions in chat_bot/README.md
```

## 📚 Documentation

- **[chat_bot/README.md](chat_bot/README.md)** - Main application documentation
- **[chat_bot/GCP_DEPLOYMENT.md](chat_bot/GCP_DEPLOYMENT.md)** - GCP Cloud Run deployment guide
- **[chat_bot/DOCKER.md](chat_bot/DOCKER.md)** - Docker setup and usage

## 🛠️ Features

- ☕ **Coffee-Themed Design**: Beautiful warm color scheme with sidebar navigation
- 🤖 **AI-Powered Chat**: Powered by OpenAI GPT models
- 📧 **Gmail Integration**: Read and manage emails with ScaleKit
- 📅 **Calendar Integration**: Manage Google Calendar events
- 📝 **Notion Integration**: Create and search Notion pages
- 🔌 **Smart Tool Integration**: AI automatically uses available tools
- 🐳 **Docker Ready**: Easy containerization and deployment
- 🔒 **Secure**: OAuth-based authentication through ScaleKit

## 📋 Requirements

- Python 3.10+
- OpenAI API key
- ScaleKit credentials (Client ID, Client Secret, Environment URL)
- Docker (optional, for containerized deployment)

## 🔗 Links

- **Main Application**: See [chat_bot/README.md](chat_bot/README.md)
- **Deployment Guide**: See [chat_bot/GCP_DEPLOYMENT.md](chat_bot/GCP_DEPLOYMENT.md)

## 📝 License

This is a sample application for demonstration purposes.
