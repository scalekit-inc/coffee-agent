# 🐳 Docker Setup for Coffee Agent

This guide will help you build and run the Coffee Agent application using Docker for local testing and GCP deployment.

## 📋 Prerequisites

- Docker installed on your machine
- Docker Compose installed
- API keys configured in `.env` file

## 🔧 Environment Setup

Create a `.env` file in the project root with your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
SCALEKIT_CLIENT_ID=your_scalekit_client_id_here
SCALEKIT_CLIENT_SECRET=your_scalekit_client_secret_here
SCALEKIT_ENV_URL=https://kindle-dev.scalekit.cloud
```

## 🚀 Quick Start

### Option 1: Using the provided script (Recommended)

```bash
./docker-run.sh
```

This script will:
- Check for the `.env` file
- Build the Docker image
- Start the application
- Provide useful commands

### Option 2: Manual Docker commands

```bash
# Build the image
docker build -t chat-bot-app .

# Run with docker-compose
docker-compose up -d

# Or run directly with Docker
docker run -p 8000:8000 --env-file .env chat-bot-app
```

## 📱 Access the Application

Once running, access the application at:
- **Local**: http://localhost:8000
- **Network**: http://your-ip:8000
- **Production**: (Update with your Cloud Run URL after deployment)

## 🛠️ Useful Commands

### View logs
```bash
# Follow logs in real-time
docker-compose logs -f

# View recent logs
docker-compose logs --tail=100
```

### Stop the application
```bash
docker-compose down
```

### Restart the application
```bash
docker-compose restart
```

### Rebuild and restart
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check container status
```bash
docker-compose ps
```

## 🔍 Troubleshooting

### Port already in use
If port 8000 is already in use, modify the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Environment variables not loading
Make sure your `.env` file is in the project root and contains all required variables.

### Build fails
Try rebuilding without cache:
```bash
docker build --no-cache -t chat-bot-app .
```

### Container won't start
Check the logs for errors:
```bash
docker-compose logs
```

## 🏗️ Production Considerations

For production deployment:

1. **Security**: The Dockerfile creates a non-root user for security
2. **Health Checks**: Built-in health checks monitor application status
3. **Gunicorn**: Production-grade WSGI server with multiple workers
4. **Environment**: Set `FLASK_ENV=production` for production

## 📦 Image Details

- **Base Image**: Python 3.11-slim
- **Port**: 8000
- **User**: Non-root user (appuser)
- **Health Check**: HTTP endpoint check every 30s
- **Workers**: 2 Gunicorn workers
- **Timeout**: 120 seconds

## 🔄 Development Workflow

For development with live code changes:

```bash
# Run with volume mounting for live reload
docker-compose up -d

# View logs while developing
docker-compose logs -f
```

The application will automatically reload when you make changes to the code.
