"""
File utility functions for handling temporary files and file operations.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def get_file_size(file_path: str) -> str:
        """Get human-readable file size."""
        try:
            size_bytes = os.path.getsize(file_path)
            return FileUtils.format_file_size(size_bytes)
        except OSError:
            return "Unknown"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        size_index = 0
        size_value = float(size_bytes)
        
        while size_value >= 1024 and size_index < len(size_names) - 1:
            size_value /= 1024
            size_index += 1
        
        if size_index == 0:
            return f"{int(size_value)} {size_names[size_index]}"
        else:
            return f"{size_value:.1f} {size_names[size_index]}"
    
    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """Safely delete a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
                return True
            return False
        except OSError as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
            return False
    
    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """Ensure directory exists, create if it doesn't."""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except OSError as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_image_file(filename: str) -> bool:
        """Check if file is an image based on extension."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif']
        extension = FileUtils.get_file_extension(filename)
        return extension in image_extensions
    
    @staticmethod
    def get_temp_filename(prefix: str = "temp", suffix: str = "") -> str:
        """Generate a temporary filename."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{unique_id}{suffix}"
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_hours: int = 1) -> int:
        """Clean up old files from directory."""
        import time
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        if FileUtils.cleanup_file(file_path):
                            cleaned_count += 1
                            
        except OSError as e:
            logger.error(f"Error cleaning up old files: {e}")
        
        return cleaned_count
