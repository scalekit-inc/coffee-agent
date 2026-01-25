# ☕ Coffee Agent

A modern, coffee-themed AI chat application built with Flask and OpenAI, featuring a beautiful sidebar layout and designed for easy deployment in Docker containers.

## 🌐 Live Application

**Production URL**: (Update with your deployment URL)

## Features

- ☕ **Coffee-Themed Design**: Beautiful warm color scheme with sidebar navigation
- 🤖 **AI-Powered Chat**: Powered by OpenAI GPT models
- 📧 **Gmail Integration**: Read and manage emails with ScaleKit
- 📅 **Calendar Integration**: Manage Google Calendar events
- 📝 **Notion Integration**: Create and search Notion pages
- 🔌 **Smart Tool Integration**: AI automatically uses Gmail/Calendar/Notion tools when available
- 💬 **Real-time Chat Interface**: Modern, responsive chat UI with sidebar layout
- 🎨 **Beautiful Design**: Coffee-themed interface with elegant typography
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🐳 **Docker Ready**: Easy containerization and deployment
- 🔒 **Secure**: Non-root user and health checks

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI**: OpenAI GPT API
- **Container**: Docker with Gunicorn
- **Styling**: Modern CSS with gradients and animations

## Quick Start

### Prerequisites

- **Python 3.10+** (required for ScaleKit integration)
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- ScaleKit credentials (for Gmail integration)
- Virtual environment support (built into Python 3.3+)

### Environment Setup

1. Create a `.env` file in the root directory:
```bash
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# ScaleKit Configuration (Required for Gmail, Calendar, and Notion integrations)
SCALEKIT_CLIENT_ID=your_scalekit_client_id_here
SCALEKIT_CLIENT_SECRET=your_scalekit_client_secret_here
SCALEKIT_ENV_URL=https://kindle-dev.scalekit.cloud

# Optional: Custom port (default: 8000)
# PORT=8000
```

### Local Development

1. **Setup virtual environment and install dependencies:**

   **On macOS/Linux:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   **On Windows:**
   ```cmd
   setup.bat
   ```

   **Manual setup:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate.bat  # On Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Activate virtual environment (if not already activated):**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate.bat  # On Windows
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Open your browser and navigate to `http://localhost:8000`**

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run manually:
```bash
docker build -t chat-bot .
docker run -p 5000:5000 --env-file .env chat-bot
```

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message and get AI response
- `GET /api/health` - Health check endpoint

### Integration Endpoints

**Gmail:**
- `GET /api/gmail/status` - Get Gmail connection status
- `POST /api/gmail/enable` - Enable Gmail integration

**Calendar:**
- `GET /api/calendar/status` - Get Calendar connection status
- `POST /api/calendar/enable` - Enable Calendar integration

**Notion:**
- `GET /api/notion/status` - Get Notion connection status
- `POST /api/notion/enable` - Enable Notion integration

## Project Structure

```
chat_bot/
├── app.py                 # Main Flask application
├── run.py                 # Development startup script
├── gmail_integration.py   # Gmail integration module
├── calendar_integration.py  # Google Calendar integration module
├── notion_integration.py    # Notion integration module
├── scalekit_client.py       # Shared ScaleKit client
├── requirements.txt       # Python dependencies
├── setup.sh              # Unix/macOS setup script
├── setup.bat             # Windows setup script
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .dockerignore         # Docker ignore file
├── .gitignore            # Git ignore patterns
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Modern CSS styles
│   └── js/
│       └── script.js     # Chat functionality
└── README.md             # This file
```

## Integrations

### Setup Integrations

1. **Get ScaleKit Credentials:**
   - Obtain `SCALEKIT_CLIENT_ID` and `SCALEKIT_CLIENT_SECRET` from ScaleKit
   - Set the `SCALEKIT_ENV_URL` (default: `https://kindle-dev.scalekit.cloud`)

2. **Enable Integrations:**
   - Toggle the integration switches in the chat interface sidebar
   - Click the authorization link when prompted
   - Complete OAuth flow for each integration
   - Return to the chat and toggle again

### Gmail Integration

**Capabilities:**
- 📧 **Read Emails**: Fetch latest emails from inbox
- 🔍 **Search Emails**: Filter by sender, subject, or Gmail search queries
- 📊 **Smart Summaries**: AI processes email content and provides insights

**Usage Examples:**
- "read my latest emails"
- "check unread messages"
- "find emails from john@example.com"

### Calendar Integration

**Capabilities:**
- 📅 **View Events**: Fetch calendar events for specific dates
- ➕ **Create Events**: Schedule new calendar events
- 🔍 **Search Events**: Find events by date or query

**Usage Examples:**
- "show my calendar events for today"
- "create a meeting tomorrow at 2pm"
- "what's on my calendar this week"

### Notion Integration

**Capabilities:**
- 📝 **Create Pages**: Create new pages in Notion workspace
- 🔍 **Search Pages**: Search and retrieve Notion pages

**Usage Examples:**
- "create a Notion page titled 'Meeting Notes'"
- "search for pages about 'project planning'"

## Customization

### Changing the AI Model

Edit `app.py` and modify the model parameter in the OpenAI API call:

```python
response = client.chat.completions.create(
    model="gpt-4",  # Change to your preferred model
    messages=messages,
    max_tokens=1000,
    temperature=0.7
)
```

### Styling

The CSS is organized with modern practices:
- CSS custom properties for easy theming
- Responsive design with mobile-first approach
- Smooth animations and transitions
- Modern gradient backgrounds

## Deployment

### Production Considerations

- Use environment variables for sensitive data
- Set `FLASK_ENV=production`
- Configure proper logging
- Use reverse proxy (nginx) for production
- Set up SSL/TLS certificates

### Docker Production

```bash
# Build production image
docker build -t chat-bot:production .

# Run with production settings
docker run -d \
  -p 80:5000 \
  --env-file .env \
  --name chat-bot-prod \
  chat-bot:production
```

## Health Checks

The application includes health check endpoints for container orchestration:

- **Docker Health Check**: Built into the Dockerfile
- **API Health Endpoint**: `/api/health`
- **Status Monitoring**: Returns service status and health information

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your `.env` file contains the correct API key
2. **Port Already in Use**: Change the port in `docker-compose.yml` or `app.py`
3. **Docker Build Failures**: Ensure you have sufficient disk space and Docker is running

### Logs

Check Docker logs:
```bash
docker-compose logs chat-bot
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the code comments
- Open an issue on the repository
