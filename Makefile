# Makefile for Telegram Image Enhancement Bot

.PHONY: help build run stop logs clean dev prod restart status

# Default target
help:
	@echo "Telegram Image Enhancement Bot - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  build    - Build Docker images"
	@echo "  run      - Run the bot in development mode"
	@echo "  prod     - Run the bot in production mode with nginx"
	@echo "  stop     - Stop all containers"
	@echo "  restart  - Restart all containers"
	@echo "  logs     - Show container logs"
	@echo "  status   - Show container status"
	@echo "  clean    - Remove containers and images"
	@echo "  dev      - Start development environment"
	@echo ""
	@echo "Before running, make sure to:"
	@echo "  1. Copy .env.example to .env"
	@echo "  2. Set your TELEGRAM_BOT_TOKEN in .env"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Run in development mode (bot + webhook server only)
run: build
	@echo "Starting Telegram Bot in development mode..."
	docker-compose up -d telegram-bot webhook-server
	@echo "Bot is running at http://localhost:5000"
	@echo "Webhook server is running at http://localhost:5001"

# Run in production mode (with nginx)
prod: build
	@echo "Starting Telegram Bot in production mode..."
	docker-compose up -d
	@echo "Production setup is running:"
	@echo "  - Web interface: http://localhost"
	@echo "  - Bot status: http://localhost/api/bot/status"
	@echo "  - Webhook endpoint: http://localhost/webhook"

# Stop all containers
stop:
	@echo "Stopping all containers..."
	docker-compose down

# Restart all containers
restart: stop run

# Show logs
logs:
	docker-compose logs -f --tail=100

# Show specific service logs
logs-bot:
	docker-compose logs -f --tail=100 telegram-bot

logs-webhook:
	docker-compose logs -f --tail=100 webhook-server

logs-nginx:
	docker-compose logs -f --tail=100 nginx

# Show container status
status:
	docker-compose ps

# Clean up containers and images
clean:
	@echo "Cleaning up containers and images..."
	docker-compose down --volumes --remove-orphans
	docker system prune -f
	docker volume prune -f

# Development environment setup
dev:
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file and set your TELEGRAM_BOT_TOKEN"; \
	fi
	$(MAKE) run

# Quick commands
up: run
down: stop
rebuild: clean build run

# Check if bot is working
test:
	@echo "Testing bot connectivity..."
	@curl -s http://localhost:5001/api/bot/status | python -m json.tool || echo "Bot not responding"

# View webhook info
webhook-info:
	@echo "Getting webhook information..."
	@curl -s http://localhost:5001/api/webhook/info | python -m json.tool || echo "Webhook server not responding"

# Set webhook (requires WEBHOOK_URL environment variable)
webhook-set:
	@if [ -z "$(WEBHOOK_URL)" ]; then \
		echo "Please provide WEBHOOK_URL: make webhook-set WEBHOOK_URL=https://your-domain.com/webhook"; \
	else \
		echo "Setting webhook to $(WEBHOOK_URL)..."; \
		curl -X POST http://localhost:5001/api/webhook/set \
			-H "Content-Type: application/json" \
			-d '{"url":"$(WEBHOOK_URL)"}' | python -m json.tool; \
	fi

# Delete webhook
webhook-delete:
	@echo "Deleting webhook..."
	@curl -X DELETE http://localhost:5001/api/webhook/delete | python -m json.tool

# Show recent activities
activities:
	@echo "Recent bot activities:"
	@curl -s http://localhost:5001/api/activity/recent | python -m json.tool || echo "Webhook server not responding"