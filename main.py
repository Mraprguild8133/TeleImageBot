#!/usr/bin/env python3
"""
Telegram Image Enhancement Bot
Main entry point for the bot application.
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import BotHandlers
from config import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot."""
    # Get bot token from environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required!")
        return
    PORT = int(os.environ.get("PORT", 8443))
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Initialize handlers
    bot_handlers = BotHandlers()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot_handlers.start))
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.PHOTO, bot_handlers.handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, bot_handlers.handle_document))
    
    # Add callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(bot_handlers.handle_callback))
    
    # Add error handler
    application.add_error_handler(bot_handlers.error_handler)
    
    logger.info("Starting bot...")
    
    # Start the bot using run_polling which handles the event loop internally
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
