#!/usr/bin/env python3
"""
Integration layer to connect the existing Telegram bot with the webhook server.
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import BotHandlers
from config import Config

# Import webhook server functions
try:
    from webhook_server import increment_processed_images, add_active_user, add_activity
except ImportError:
    # Fallback functions if webhook server is not running
    def increment_processed_images():
        pass
    def add_active_user(user_id):
        pass
    def add_activity(action, details, activity_type='info'):
        pass

logger = logging.getLogger(__name__)

class EnhancedBotHandlers(BotHandlers):
    """Enhanced bot handlers with webhook server integration."""
    
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()
    
    async def start(self, update: Update, context):
        """Enhanced start handler with logging."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        add_active_user(user_id)
        add_activity('User Started Bot', f'User @{username} ({user_id}) started the bot', 'info')
        
        await super().start(update, context)
    
    async def handle_photo(self, update: Update, context):
        """Enhanced photo handler with statistics tracking."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        add_active_user(user_id)
        add_activity('Image Uploaded', f'User @{username} uploaded a photo', 'info')
        
        await super().handle_photo(update, context)
    
    async def handle_document(self, update: Update, context):
        """Enhanced document handler with statistics tracking."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        add_active_user(user_id)
        add_activity('Document Uploaded', f'User @{username} uploaded a document', 'info')
        
        await super().handle_document(update, context)
    
    async def handle_callback(self, update: Update, context):
        """Enhanced callback handler with processing tracking."""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        callback_data = query.data
        
        add_active_user(user_id)
        
        # Log the processing type
        processing_types = {
            'enhance_hd': 'HD Enhancement',
            'enhance_4k': '4K Enhancement',
            'enhance_4k_compressed': '4K Compressed Enhancement',
            'optimize': 'Image Optimization',
            'convert_format': 'Format Conversion'
        }
        
        processing_type = processing_types.get(callback_data, callback_data)
        add_activity('Processing Started', f'User @{username} started {processing_type}', 'info')
        
        # Call parent handler
        await super().handle_callback(update, context)
        
        # After processing, increment counter if it was successful
        if callback_data in processing_types:
            increment_processed_images()
            add_activity('Processing Completed', f'{processing_type} completed for @{username}', 'success')

def create_enhanced_application():
    """Create the enhanced Telegram application with webhook server integration."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required!")
        return None
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Initialize enhanced handlers
    bot_handlers = EnhancedBotHandlers()
    
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
    
    logger.info("Enhanced bot application created with webhook server integration")
    add_activity('Bot Initialized', 'Enhanced bot handlers loaded', 'success')
    
    return application

def main():
    """Main function to run the enhanced bot."""
    application = create_enhanced_application()
    if not application:
        return
    
    logger.info("Starting enhanced bot...")
    add_activity('Bot Started', 'Enhanced Telegram bot started', 'success')
    
    # Start the bot using run_polling which handles the event loop internally
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()