# Development Workflow

This guide covers the development workflow for the Coffee Agent project.

## 🚀 Quick Start for Developers

### First Time Setup

1. **Clone and navigate to the project:**
   ```bash
   cd chat_bot
   ```

2. **Run the automated setup:**
   ```bash
   # On macOS/Linux
   ./setup.sh
   
   # On Windows
   setup.bat
   ```

3. **Create your environment file:**
   ```bash
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   ```

4. **Start development:**
   ```bash
   python run.py
   ```

### Daily Development Workflow

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate.bat  # Windows
   ```

2. **Make your changes to the code**

3. **Test your changes:**
   ```bash
   python run.py
   ```

4. **Deactivate when done:**
   ```bash
   deactivate
   ```

## 🔧 Development Commands

### Virtual Environment Management

```bash
# Create new virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate.bat  # Windows

# Deactivate
deactivate

# Remove virtual environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

### Package Management

```bash
# Install new package
pip install package_name

# Add to requirements.txt
pip freeze > requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt
```

### Running the Application

```bash
# Development mode (with auto-reload)
python run.py

# Production mode
python app.py

# With specific port
python app.py --port 8000
```

## 📁 Project Structure Explained

```
chat_bot/
├── app.py                 # Main Flask application (production)
├── run.py                 # Development server with debug mode
├── setup.sh               # Unix/macOS setup automation
├── setup.bat              # Windows setup automation
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore patterns
├── templates/             # HTML templates
├── static/                # Static assets (CSS, JS, images)
└── Dockerfile             # Container configuration
```

## 🐛 Debugging

### Common Issues

1. **Virtual environment not activated:**
   ```bash
   # Check if activated (should show venv path)
   which python
   # or on Windows
   where python
   ```

2. **Port already in use:**
   ```bash
   # Find process using port 5000
   lsof -i :5000  # macOS/Linux
   netstat -ano | findstr :5000  # Windows
   ```

3. **OpenAI API key error:**
   - Check `.env` file exists
   - Verify API key is correct
   - Ensure no extra spaces or quotes

### Debug Mode

The `run.py` script runs in debug mode by default:
- Auto-reloads on code changes
- Detailed error messages
- Debug console in browser

## 🧪 Testing

### Manual Testing
1. Start the application
2. Open browser to `http://localhost:8000`
3. Send test messages
4. Check browser console for errors

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/health
# Production: curl https://YOUR-SERVICE-NAME-PROJECT-ID.REGION.run.app/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
# Production: curl -X POST https://YOUR-SERVICE-NAME-PROJECT-ID.REGION.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, AI!"}'
```

## 🚢 Deployment Preparation

### Before Committing
1. Ensure virtual environment is not committed
2. Check `.gitignore` includes all necessary patterns
3. Test with production settings (`python app.py`)

### Docker Testing
```bash
# Build and test container
docker build -t chat-bot:test .
docker run -p 5000:5000 --env-file .env chat-bot:test

# Test with docker-compose
docker-compose up --build
```

## 📝 Code Style

- Use consistent indentation (4 spaces)
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused

## 🔄 Version Control

### Git Workflow
```bash
# Check status
git status

# Add changes
git add .

# Commit with meaningful message
git commit -m "Add feature: user authentication"

# Push changes
git push origin main
```

### Branch Strategy
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Emergency fixes

## 📚 Useful Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
