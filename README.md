# Telegram Image Enhancement Bot 🤖

A powerful Telegram bot that provides automated image processing services including HD upscaling, 4K enhancement, format conversion, and size optimization. Built with Python using the `python-telegram-bot` library and containerized with Docker for easy deployment.

## Features

- **HD Quality Enhancement** (1920x1080) - Standard HD upscaling
- **4K Quality Enhancement** (3840x2160) - High-quality 4K upscaling  
- **4K Compressed** - 4K resolution with optimized file size
- **Image Optimization** - Smart size reduction while maintaining quality
- **Format Conversion** - Convert between JPEG, PNG, WebP, BMP, TIFF
- **Web Dashboard** - Real-time monitoring and webhook management
- **Webhook Support** - Production-ready webhook handling
- **Docker Support** - Containerized deployment with nginx proxy

## Quick Start with Docker

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd telegram-image-bot
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file and add your bot token:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
SECRET_KEY=your_random_secret_key
```

### 3. Run with Docker
```bash
# Development mode (bot + web dashboard)
make dev

# Or production mode (with nginx proxy)
make prod
```

### 4. Access Your Bot
- **Web Dashboard**: http://localhost (production) or http://localhost:5001 (development)
- **Bot Status API**: http://localhost/api/bot/status
- **Webhook Endpoint**: http://localhost/webhook

## Docker Commands

```bash
# Quick setup and run
make dev                    # Setup development environment
make run                    # Run bot + webhook server
make prod                   # Run with nginx proxy

# Management
make status                 # Show container status
make logs                   # View all logs  
make logs-bot               # View bot logs only
make restart                # Restart all services
make stop                   # Stop all containers
make clean                  # Remove containers and cleanup

# Webhook management
make webhook-info           # Get current webhook status
make webhook-set WEBHOOK_URL=https://your-domain.com/webhook
make webhook-delete         # Switch back to polling

# Testing
make test                   # Test bot connectivity
make activities             # Show recent bot activities
```

## Manual Setup (Without Docker)

### Requirements
- Python 3.11+
- pip or uv package manager

### Installation
```bash
# Install dependencies
pip install python-telegram-bot==20.7 pillow opencv-python numpy flask

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"

# Run the bot
python main.py

# Run webhook server (separate terminal)
python webhook_server.py
```

## Architecture

### Components
- **Bot Handler** (`main.py`) - Main Telegram bot application
- **Image Processor** (`bot/image_processor.py`) - Core image processing logic
- **Webhook Server** (`webhook_server.py`) - Web dashboard and webhook handling
- **Web Interface** (`templates/index.html`) - Real-time monitoring dashboard

### Processing Pipeline
1. **Image Upload** - Users send images via Telegram
2. **Enhancement Options** - Interactive keyboard with processing choices
3. **Processing** - Asynchronous image processing with progress updates
4. **Delivery** - Enhanced images sent back to users
5. **Cleanup** - Automatic temporary file cleanup

### Deployment Modes
- **Polling Mode** - Bot actively polls Telegram for updates (default)
- **Webhook Mode** - Telegram sends updates to your server (production)

## Configuration

### Environment Variables
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional
SECRET_KEY=your_secret_key              # For webhook security
PORT=5000                               # Server port
LOG_LEVEL=INFO                          # Logging level
MAX_FILE_SIZE=20                        # Max upload size (MB)
WEBHOOK_DOMAIN=https://your-domain.com  # For auto webhook setup
```

### Bot Configuration
Edit `config.py` to customize:
- Image processing parameters
- File size limits
- Supported formats
- Concurrency settings

## Web Dashboard Features

### Real-time Monitoring
- Bot status and uptime
- Images processed counter
- Active users tracking
- Recent activities log

### Webhook Management
- Set/delete webhooks
- View webhook status
- Auto-generate webhook URLs
- Security token management

### Activity Logging
- User interactions
- Processing activities
- Error tracking
- Performance metrics

## Production Deployment

### 1. Prepare Server
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your repository
git clone <your-repo-url>
cd telegram-image-bot
```

### 2. Configure Environment
```bash
# Create production environment file
cp .env.example .env
nano .env  # Add your production values
```

### 3. Setup SSL (Optional)
```bash
# Add your SSL certificates to ./ssl/ directory
mkdir ssl
# Copy your cert.pem and key.pem files
# Uncomment HTTPS section in nginx.conf
```

### 4. Deploy
```bash
# Start production environment
make prod

# Verify deployment
make status
make test
```

### 5. Set Webhook
```bash
# Set webhook for production
make webhook-set WEBHOOK_URL=https://your-domain.com/webhook

# Verify webhook
make webhook-info
```

## Development

### Project Structure
```
telegram-image-bot/
├── bot/                    # Bot handlers and logic
│   ├── handlers.py        # Message and callback handlers
│   ├── image_processor.py # Image processing engine
│   └── keyboards.py       # Telegram inline keyboards
├── static/                # Web assets
│   ├── css/style.css     # Dashboard styling
│   └── js/webhook.js     # Dashboard functionality
├── templates/             # HTML templates
│   └── index.html        # Main dashboard
├── utils/                 # Utilities
│   └── file_utils.py     # File management helpers
├── main.py               # Main bot application
├── webhook_server.py     # Web dashboard server
├── config.py            # Configuration
├── docker-compose.yml   # Docker services
└── Dockerfile          # Container definition
```

### Adding New Features
1. **Image Processing**: Extend `ImageProcessor` class
2. **Bot Commands**: Add handlers in `BotHandlers` class  
3. **Web API**: Add endpoints in `webhook_server.py`
4. **UI Components**: Update `templates/index.html`

### Testing
```bash
# Test bot locally
python main.py

# Test webhook server
python webhook_server.py

# Test with Docker
make test
```

## Troubleshooting

### Common Issues

**Bot Token Invalid**
```bash
# Verify token format: 123456789:ABCDEF...
# Get new token from @BotFather if needed
```

**Port Already in Use**
```bash
# Change port in docker-compose.yml or .env
# Or stop conflicting services
```

**Webhook SSL Issues**
```bash
# Ensure HTTPS with valid certificate
# Check nginx SSL configuration
# Verify webhook URL is accessible
```

**Image Processing Fails**
```bash
# Check Docker container resources
# Verify OpenCV installation
# Monitor container logs: make logs-bot
```

### Monitoring
```bash
# Container health
make status

# Application logs
make logs

# Bot connectivity
make test

# Recent activities
make activities
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: Check this README and code comments
- **Issues**: Create GitHub issues for bugs
- **Telegram**: Contact @BotFather for bot-related issues

---

Made with ❤️ for the Telegram community