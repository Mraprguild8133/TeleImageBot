# Overview

This is a Telegram Image Enhancement Bot that provides automated image processing services through Telegram's messaging platform. The bot allows users to upload images and enhance them with various quality improvements including HD upscaling (1920x1080), 4K upscaling (3840x2160), file size optimization, and format conversion. The application is built using Python's `python-telegram-bot` library and integrates computer vision libraries for image processing tasks.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework Architecture
The application follows a modular handler-based architecture using the `python-telegram-bot` framework. The main entry point (`main.py`) initializes the Telegram application and registers various handlers for different message types (commands, photos, documents, callback queries). This design separates concerns by delegating specific functionality to dedicated handler classes.

## Image Processing Pipeline
The core image processing functionality is encapsulated in the `ImageProcessor` class, which uses a combination of PIL (Python Imaging Library) and OpenCV for image manipulation. The system implements asynchronous processing to prevent blocking the main bot thread during computationally intensive operations. Images are processed in a dedicated thread pool using asyncio's `run_in_executor` method.

## User Interface Design
The bot uses Telegram's inline keyboards to provide an interactive menu system. The `Keyboards` class defines various keyboard layouts for different processing options (HD/4K enhancement, format conversion, quality selection). This creates a guided user experience where users can select processing options through button interactions rather than text commands.

## File Management Strategy
Temporary file handling is managed through the `FileUtils` class, which provides utilities for file size calculation, formatting, and cleanup operations. The system uses a designated temporary directory (`/tmp/bot_images`) for storing intermediate files during processing, with automatic cleanup mechanisms to prevent storage accumulation.

## Configuration Management
All bot settings, processing parameters, and user-facing messages are centralized in a configuration class. This includes file size limits (20MB), supported image formats (JPEG, PNG, WebP, BMP, TIFF), resolution targets, and concurrency limits. The configuration uses environment variables for sensitive data like bot tokens.

## Error Handling and Logging
The application implements comprehensive error handling throughout the processing pipeline, with structured logging to track operations and debug issues. Telegram-specific errors are caught and handled gracefully to maintain bot responsiveness.

# External Dependencies

## Telegram Bot API
- **python-telegram-bot**: Primary framework for interacting with Telegram's Bot API, handling message routing, callback queries, and file operations
- **TELEGRAM_BOT_TOKEN**: Environment variable containing the bot's authentication token from Telegram's BotFather

## Image Processing Libraries
- **PIL (Pillow)**: Core image processing library for format conversion, resizing, and basic image enhancements
- **OpenCV (cv2)**: Computer vision library used for advanced image processing algorithms and quality enhancement
- **NumPy**: Numerical computing library supporting OpenCV operations and array manipulations

## System Dependencies
- **asyncio**: Python's built-in asynchronous I/O framework for non-blocking operations
- **logging**: Standard Python logging for application monitoring and debugging
- **os**: Operating system interface for file operations and environment variable access

## Processing Infrastructure
The bot is designed to handle concurrent image processing with configurable limits (max 3 concurrent processes) and uses the local filesystem for temporary storage during processing operations.

# Recent Updates

## August 6, 2025
- **Fixed 4K Processing**: Enhanced 4K upscaling with improved error handling and detailed logging
- **Added 4K Compressed Option**: New processing mode that provides 4K resolution with smaller file sizes (75% quality vs 95%)
- **Multi-step Upscaling**: Added conservative scaling approach for large image upscaling to prevent memory issues
- **Error Recovery**: Improved fallback mechanisms when 4K processing encounters issues
- **Performance Optimization**: Reduced bilateral filter intensity for better performance on large images
- **User Feedback**: Added specific error messages for 4K processing failures with alternative suggestions
- **Enhanced UI**: Updated keyboard layout with 5 processing options including the new 4K Compressed mode
- **Web Dashboard**: Created comprehensive Flask-based web interface for bot monitoring and webhook management
- **Docker Integration**: Complete containerization with Docker Compose, nginx proxy, and production deployment setup
- **Webhook Management**: Full webhook support with web UI for configuration and monitoring
- **Real-time Monitoring**: Live bot status, activity tracking, and performance metrics dashboard
- **Custom Upscaling**: Added flexible upscaling system with 2x, 3x, 4x, 8x options and Smart/Max quality modes
- **Advanced Processing**: Progressive upscaling algorithms with OpenCV enhancement and transparency preservation