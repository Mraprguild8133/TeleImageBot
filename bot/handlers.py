"""
Telegram bot handlers for image processing commands and messages.
"""

import os
import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from bot.image_processor import ImageProcessor
from bot.keyboards import Keyboards
from utils.file_utils import FileUtils
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Class containing all bot message and command handlers."""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.keyboards = Keyboards()
        self.file_utils = FileUtils()
        
        # Ensure temp directory exists
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        try:
            await update.message.reply_text(
                Config.WELCOME_MESSAGE,
                parse_mode='Markdown'
            )
        except TelegramError as e:
            logger.error(f"Error sending start message: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        try:
            await update.message.reply_text(
                Config.HELP_MESSAGE,
                parse_mode='Markdown'
            )
        except TelegramError as e:
            logger.error(f"Error sending help message: {e}")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo messages (compressed images)."""
        try:
            photo = update.message.photo[-1]  # Get highest resolution version
            
            # Check file size
            if photo.file_size > Config.MAX_FILE_SIZE:
                await update.message.reply_text(
                    "❌ Image too large! Please send an image smaller than 20MB."
                )
                return
            
            # Send processing message
            processing_msg = await update.message.reply_text(
                "📥 Downloading image... Please wait."
            )
            
            # Download the file
            file = await context.bot.get_file(photo.file_id)
            file_path = os.path.join(Config.TEMP_DIR, f"{photo.file_id}.jpg")
            await file.download_to_drive(file_path)
            
            # Store file info in context
            context.user_data['current_image'] = {
                'file_path': file_path,
                'original_filename': f"image_{photo.file_id}.jpg",
                'file_id': photo.file_id
            }
            
            # Update message with options
            await processing_msg.edit_text(
                "✅ Image downloaded! Choose processing option:",
                reply_markup=self.keyboards.get_processing_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error handling photo: {e}")
            await update.message.reply_text(
                "❌ Error processing image. Please try again."
            )
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document messages (uncompressed images)."""
        try:
            document = update.message.document
            
            # Check if it's an image
            if not document.mime_type or not document.mime_type.startswith('image/'):
                await update.message.reply_text(
                    "❌ Please send an image file (JPEG, PNG, WebP, BMP, TIFF)."
                )
                return
            
            # Check file size
            if document.file_size > Config.MAX_FILE_SIZE:
                await update.message.reply_text(
                    "❌ Image too large! Please send an image smaller than 20MB."
                )
                return
            
            # Send processing message
            processing_msg = await update.message.reply_text(
                "📥 Downloading image... Please wait."
            )
            
            # Download the file
            file = await context.bot.get_file(document.file_id)
            file_extension = os.path.splitext(document.file_name)[1].lower()
            file_path = os.path.join(Config.TEMP_DIR, f"{document.file_id}{file_extension}")
            await file.download_to_drive(file_path)
            
            # Store file info in context
            context.user_data['current_image'] = {
                'file_path': file_path,
                'original_filename': document.file_name,
                'file_id': document.file_id
            }
            
            # Update message with options
            await processing_msg.edit_text(
                "✅ Image downloaded! Choose processing option:",
                reply_markup=self.keyboards.get_processing_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await update.message.reply_text(
                "❌ Error processing image. Please try again."
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        try:
            # Check if user has uploaded an image
            if 'current_image' not in context.user_data:
                await query.edit_message_text(
                    "❌ No image found. Please upload an image first."
                )
                return
            
            image_info = context.user_data['current_image']
            callback_data = query.data
            
            # Show processing message
            await query.edit_message_text("🔄 Processing image... This may take a moment.")
            
            # Process image based on callback data
            result_path = None
            
            if callback_data == "enhance_hd":
                result_path = await self.image_processor.enhance_to_hd(image_info['file_path'])
                quality_text = "HD (1920x1080)"
                
            elif callback_data == "enhance_4k":
                logger.info(f"Starting 4K enhancement for user")
                result_path = await self.image_processor.enhance_to_4k(image_info['file_path'])
                if result_path:
                    logger.info(f"4K enhancement successful: {result_path}")
                    quality_text = "4K (3840x2160)"
                else:
                    logger.error("4K enhancement failed - result_path is None")
                    await query.edit_message_text(
                        "❌ 4K processing failed. The image might be too large or there was a processing error. Please try HD quality instead."
                    )
                    return
                    
            elif callback_data == "enhance_4k_compressed":
                logger.info(f"Starting 4K compressed enhancement for user")
                result_path = await self.image_processor.enhance_to_4k_compressed(image_info['file_path'])
                if result_path:
                    logger.info(f"4K compressed enhancement successful: {result_path}")
                    quality_text = "4K Compressed (3840x2160)"
                else:
                    logger.error("4K compressed enhancement failed - result_path is None")
                    await query.edit_message_text(
                        "❌ 4K compressed processing failed. Please try HD quality instead."
                    )
                    return
                
            elif callback_data == "optimize":
                result_path = await self.image_processor.optimize_image(image_info['file_path'])
                quality_text = "Optimized"
                
            elif callback_data == "convert_format":
                await query.edit_message_text(
                    "Choose output format:",
                    reply_markup=self.keyboards.get_format_keyboard()
                )
                return
            
            elif callback_data == "custom_upscale":
                await query.edit_message_text(
                    "🔍 Choose upscaling option:",
                    reply_markup=self.keyboards.get_upscale_keyboard()
                )
                return
                
            elif callback_data.startswith("format_"):
                format_type = callback_data.split("_")[1].upper()
                result_path = await self.image_processor.convert_format(
                    image_info['file_path'], 
                    format_type
                )
                quality_text = f"Converted to {format_type}"
            
            elif callback_data.startswith("upscale_"):
                upscale_type = callback_data.split("_", 1)[1]  # Use maxsplit=1 to handle "max" properly
                
                if upscale_type in ["2x", "3x", "4x", "8x"]:
                    # Extract scale factor (e.g., "2x", "4x")
                    scale_factor = int(upscale_type[:-1])
                    mode = "standard"
                elif upscale_type == "smart":
                    scale_factor = 2  # Default 2x for smart upscale
                    mode = "smart"
                elif upscale_type == "max":
                    scale_factor = 4  # Default 4x for max quality
                    mode = "max"
                else:
                    scale_factor = 2
                    mode = "standard"
                
                logger.info(f"Processing upscale request: {upscale_type} -> {scale_factor}x {mode}")
                result_path = await self.image_processor.custom_upscale(
                    image_info['file_path'], 
                    scale_factor, 
                    mode
                )
                quality_text = f"{scale_factor}x Upscale ({mode.title()})"
            
            # Send processed image
            if result_path and os.path.exists(result_path):
                # Get file size info
                original_size = self.file_utils.get_file_size(image_info['file_path'])
                processed_size = self.file_utils.get_file_size(result_path)
                
                caption = f"✅ *Processing Complete*\n\n"
                caption += f"🎯 **Quality**: {quality_text}\n"
                caption += f"📁 **Original size**: {original_size}\n"
                caption += f"📁 **Processed size**: {processed_size}\n"
                
                # Send the processed image
                with open(result_path, 'rb') as processed_file:
                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=processed_file,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                
                # Clean up files
                self.file_utils.cleanup_file(image_info['file_path'])
                self.file_utils.cleanup_file(result_path)
                
                # Clear user data
                del context.user_data['current_image']
                
                # Edit original message
                await query.edit_message_text(
                    f"✅ {quality_text} processing completed! Check the file above."
                )
                
            else:
                await query.edit_message_text(
                    "❌ Error processing image. Please try again with a different image."
                )
                
        except Exception as e:
            logger.error(f"Error in callback handler: {e}")
            await query.edit_message_text(
                "❌ An error occurred during processing. Please try again."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors that occur during bot operation."""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Try to inform the user about the error
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An unexpected error occurred. Please try again."
                )
            except TelegramError:
                pass  # If we can't send the error message, just log it
