#!/bin/bash
set -e

# Create necessary directories
mkdir -p /tmp/bot_images /app/logs

# Set permissions
chown -R botuser:botuser /tmp/bot_images /app/logs

# Wait for dependencies if needed
if [ "$WAIT_FOR_DEPS" = "true" ]; then
    echo "Waiting for dependencies..."
    sleep 10
fi

# Check if bot token is provided
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "ERROR: TELEGRAM_BOT_TOKEN environment variable is required!"
    exit 1
fi

# Validate bot token format
if [[ ! "$TELEGRAM_BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]{35}$ ]]; then
    echo "WARNING: Bot token format seems invalid. Please verify your token."
fi

echo "Starting Telegram Image Enhancement Bot..."
echo "Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}...(hidden)"
echo "Port: ${PORT:-5000}"
echo "Mode: ${1:-bot}"

# Execute the command
exec "$@"