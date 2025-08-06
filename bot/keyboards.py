"""
Inline keyboard definitions for the Telegram bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    """Class containing inline keyboard definitions."""
    
    def get_processing_keyboard(self) -> InlineKeyboardMarkup:
        """Get the main processing options keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🎯 HD Quality", callback_data="enhance_hd"),
                InlineKeyboardButton("🎯 4K Quality", callback_data="enhance_4k")
            ],
            [
                InlineKeyboardButton("📦 4K Compressed", callback_data="enhance_4k_compressed"),
                InlineKeyboardButton("🔍 Custom Upscale", callback_data="custom_upscale")
            ],
            [
                InlineKeyboardButton("⚡ Optimize Size", callback_data="optimize"),
                InlineKeyboardButton("🔄 Convert Format", callback_data="convert_format")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_format_keyboard(self) -> InlineKeyboardMarkup:
        """Get the format conversion keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("JPEG", callback_data="format_jpeg"),
                InlineKeyboardButton("PNG", callback_data="format_png")
            ],
            [
                InlineKeyboardButton("WebP", callback_data="format_webp"),
                InlineKeyboardButton("BMP", callback_data="format_bmp")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_quality_keyboard(self) -> InlineKeyboardMarkup:
        """Get quality selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🔥 Maximum Quality", callback_data="quality_max"),
                InlineKeyboardButton("⚖️ Balanced", callback_data="quality_balanced")
            ],
            [
                InlineKeyboardButton("📦 Smaller Size", callback_data="quality_compressed"),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_upscale_keyboard(self) -> InlineKeyboardMarkup:
        """Get custom upscale options keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📈 2x Upscale", callback_data="upscale_2x"),
                InlineKeyboardButton("📈 3x Upscale", callback_data="upscale_3x")
            ],
            [
                InlineKeyboardButton("📈 4x Upscale", callback_data="upscale_4x"),
                InlineKeyboardButton("📈 8x Upscale", callback_data="upscale_8x")
            ],
            [
                InlineKeyboardButton("🎯 Smart Upscale", callback_data="upscale_smart"),
                InlineKeyboardButton("🔥 Max Upscale", callback_data="upscale_max")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
