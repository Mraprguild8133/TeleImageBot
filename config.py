"""
Configuration settings for the Telegram Image Enhancement Bot.
"""

import os

class Config:
    """Configuration class containing bot settings."""
    
    # Bot settings
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Web Service 
    PORT = os.getenv("PORTS")
    # Image processing settings
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB max file size
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP', 'BMP', 'TIFF']
    
    # Quality enhancement settings
    HD_SIZE = (1920, 1080)      # HD resolution
    UHD_4K_SIZE = (3840, 2160)  # 4K UHD resolution
    
    # Processing settings
    TEMP_DIR = "/tmp/bot_images"
    MAX_CONCURRENT_PROCESSES = 3
    
    # Messages
    WELCOME_MESSAGE = """
🎨 *Image Enhancement Bot*

Welcome! I can help you enhance and convert your images to different qualities.

📤 Send me an image and I'll provide options to:
• Convert to HD (1920x1080)
• Upscale to 4K (3840x2160)
• Optimize file size
• Change format

💡 Use /help for more information.
    """
    
    HELP_MESSAGE = """
🔧 *How to use the bot:*

1️⃣ Send me an image (photo or document)
2️⃣ Choose your preferred quality/format
3️⃣ Download the processed image

📋 *Supported formats:*
• JPEG, PNG, WebP, BMP, TIFF

📏 *Available options:*
• **HD**: 1920x1080 resolution
• **4K**: 3840x2160 resolution
• **Optimized**: Reduced file size
• **Format conversion**: Change image format

⚠️ *Limitations:*
• Maximum file size: 20MB
• Processing time varies by image size
• Some very small images may not upscale well

Need help? Contact support or report issues.
    """
