"""
Image processing functionality for quality enhancement and format conversion.
"""

import os
import logging
import asyncio
from typing import Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Class for handling image processing operations."""
    
    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
    
    async def enhance_to_hd(self, input_path: str) -> Optional[str]:
        """Enhance image to HD quality (1920x1080)."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._process_to_hd, input_path
            )
            return result
        except Exception as e:
            logger.error(f"Error enhancing to HD: {e}")
            return None
    
    async def enhance_to_4k(self, input_path: str) -> Optional[str]:
        """Enhance image to 4K quality (3840x2160)."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._process_to_4k, input_path
            )
            return result
        except Exception as e:
            logger.error(f"Error enhancing to 4K: {e}")
            return None
    
    async def enhance_to_4k_compressed(self, input_path: str) -> Optional[str]:
        """Enhance image to 4K quality with smaller file size (3840x2160)."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._process_to_4k_compressed, input_path
            )
            return result
        except Exception as e:
            logger.error(f"Error enhancing to 4K compressed: {e}")
            return None
    
    async def optimize_image(self, input_path: str) -> Optional[str]:
        """Optimize image for smaller file size while maintaining quality."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._optimize_image, input_path
            )
            return result
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
    
    async def convert_format(self, input_path: str, output_format: str) -> Optional[str]:
        """Convert image to different format."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._convert_format, input_path, output_format
            )
            return result
        except Exception as e:
            logger.error(f"Error converting format: {e}")
            return None
    
    async def custom_upscale(self, input_path: str, scale_factor: int, mode: str = "standard") -> Optional[str]:
        """Custom upscale image by specified factor."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._custom_upscale, input_path, scale_factor, mode
            )
            return result
        except Exception as e:
            logger.error(f"Error in custom upscale: {e}")
            return None
    
    def _process_to_hd(self, input_path: str) -> Optional[str]:
        """Process image to HD resolution using advanced upscaling."""
        try:
            # Load image with OpenCV for advanced processing
            img_cv = cv2.imread(input_path)
            if img_cv is None:
                # Fallback to PIL
                return self._simple_resize(input_path, Config.HD_SIZE, "HD")
            
            height, width = img_cv.shape[:2]
            target_width, target_height = Config.HD_SIZE
            
            # If image is already larger or equal, use smart resize
            if width >= target_width and height >= target_height:
                return self._smart_resize(input_path, Config.HD_SIZE, "HD")
            
            # Use EDSR (Enhanced Deep Super-Resolution) approach with available methods
            # Apply bilateral filter for noise reduction
            img_filtered = cv2.bilateralFilter(img_cv, 9, 75, 75)
            
            # Use INTER_CUBIC for upscaling
            upscaled = cv2.resize(img_filtered, Config.HD_SIZE, interpolation=cv2.INTER_CUBIC)
            
            # Apply sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(upscaled, -1, kernel)
            
            # Blend original upscaled with sharpened (70% sharpened, 30% original)
            final_img = cv2.addWeighted(upscaled, 0.3, sharpened, 0.7, 0)
            
            # Save processed image
            output_path = self._get_output_path(input_path, "HD")
            cv2.imwrite(output_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error in HD processing: {e}")
            # Fallback to simple resize
            return self._simple_resize(input_path, Config.HD_SIZE, "HD")
    
    def _process_to_4k(self, input_path: str) -> Optional[str]:
        """Process image to 4K resolution using advanced upscaling."""
        try:
            logger.info(f"Starting 4K processing for: {input_path}")
            
            # Load image with OpenCV
            img_cv = cv2.imread(input_path)
            if img_cv is None:
                logger.warning(f"Could not load image with OpenCV, using PIL fallback")
                return self._simple_resize(input_path, Config.UHD_4K_SIZE, "4K")
            
            height, width = img_cv.shape[:2]
            target_width, target_height = Config.UHD_4K_SIZE
            
            logger.info(f"Original dimensions: {width}x{height}, Target: {target_width}x{target_height}")
            
            # If image is already larger or equal, use smart resize
            if width >= target_width and height >= target_height:
                logger.info("Image is already large enough, using smart resize")
                return self._smart_resize(input_path, Config.UHD_4K_SIZE, "4K")
            
            # For very large upscaling factors, use a more conservative approach
            scale_x = target_width / width
            scale_y = target_height / height
            max_scale = max(scale_x, scale_y)
            
            logger.info(f"Scale factors: x={scale_x:.2f}, y={scale_y:.2f}, max={max_scale:.2f}")
            
            if max_scale > 8.0:
                # Use PIL for very large scaling factors
                logger.info("Very large scale factor detected, using PIL method")
                return self._simple_resize(input_path, Config.UHD_4K_SIZE, "4K")
            
            # Multi-step upscaling for better quality
            current_img = img_cv.copy()
            current_width, current_height = width, height
            step = 0
            
            # Calculate scaling steps (max 2x per step for better quality)
            while current_width < target_width or current_height < target_height:
                step += 1
                scale_factor = min(
                    2.0,
                    target_width / current_width,
                    target_height / current_height
                )
                
                new_width = int(current_width * scale_factor)
                new_height = int(current_height * scale_factor)
                
                logger.info(f"Step {step}: Scaling from {current_width}x{current_height} to {new_width}x{new_height}")
                
                # Apply bilateral filter before upscaling (reduce intensity for performance)
                current_img = cv2.bilateralFilter(current_img, 5, 50, 50)
                
                # Upscale using INTER_CUBIC
                current_img = cv2.resize(current_img, (new_width, new_height), 
                                       interpolation=cv2.INTER_CUBIC)
                
                current_width, current_height = new_width, new_height
                
                # Safety check to prevent infinite loop
                if step > 5:
                    logger.warning("Too many upscaling steps, breaking")
                    break
            
            # Final resize to exact target dimensions if needed
            if current_width != target_width or current_height != target_height:
                logger.info(f"Final resize from {current_width}x{current_height} to {target_width}x{target_height}")
                final_img = cv2.resize(current_img, Config.UHD_4K_SIZE, 
                                     interpolation=cv2.INTER_CUBIC)
            else:
                final_img = current_img
            
            # Apply moderate sharpening (reduce intensity to prevent artifacts)
            logger.info("Applying sharpening")
            gaussian = cv2.GaussianBlur(final_img, (0, 0), 1.0)
            sharpened = cv2.addWeighted(final_img, 1.2, gaussian, -0.2, 0)
            
            # Save processed image
            output_path = self._get_output_path(input_path, "4K")
            logger.info(f"Saving 4K image to: {output_path}")
            success = cv2.imwrite(output_path, sharpened, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if not success:
                logger.error("Failed to save 4K image with OpenCV")
                return None
            
            logger.info("4K processing completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in 4K processing: {e}")
            logger.info("Falling back to simple resize method")
            return self._simple_resize(input_path, Config.UHD_4K_SIZE, "4K")
    
    def _process_to_4k_compressed(self, input_path: str) -> Optional[str]:
        """Process image to 4K resolution with optimized file size."""
        try:
            logger.info(f"Starting 4K compressed processing for: {input_path}")
            
            # Use PIL for better compression control
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for JPEG compatibility
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                target_width, target_height = Config.UHD_4K_SIZE
                
                logger.info(f"Original dimensions: {original_width}x{original_height}, Target: {target_width}x{target_height}")
                
                # Calculate scale factors
                scale_x = target_width / original_width
                scale_y = target_height / original_height
                max_scale = max(scale_x, scale_y)
                
                logger.info(f"Scale factors: x={scale_x:.2f}, y={scale_y:.2f}, max={max_scale:.2f}")
                
                # For very small images that need huge upscaling, use a more conservative approach
                if max_scale > 10.0:
                    logger.info("Very large scale factor, using optimized approach")
                    # First upscale to intermediate size
                    intermediate_size = (
                        min(target_width, original_width * 4),
                        min(target_height, original_height * 4)
                    )
                    img = img.resize(intermediate_size, Image.Resampling.LANCZOS)
                
                # Final resize to target dimensions
                resized = img.resize(Config.UHD_4K_SIZE, Image.Resampling.LANCZOS)
                
                # Apply moderate enhancement
                enhancer = ImageEnhance.Sharpness(resized)
                enhanced = enhancer.enhance(1.1)
                
                # Save with optimized compression settings
                output_path = self._get_output_path(input_path, "4K_compressed")
                logger.info(f"Saving 4K compressed image to: {output_path}")
                
                # Use progressive JPEG with optimized quality for smaller file size
                enhanced.save(
                    output_path, 
                    'JPEG', 
                    quality=75,  # Lower quality for smaller file size
                    optimize=True,
                    progressive=True
                )
                
                logger.info("4K compressed processing completed successfully")
                return output_path
                
        except Exception as e:
            logger.error(f"Error in 4K compressed processing: {e}")
            logger.info("Falling back to simple resize method")
            return self._simple_resize(input_path, Config.UHD_4K_SIZE, "4K_compressed")
    
    def _optimize_image(self, input_path: str) -> Optional[str]:
        """Optimize image for smaller file size."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Get original dimensions
                original_width, original_height = img.size
                
                # Smart resize if image is very large
                max_dimension = 2048
                if max(original_width, original_height) > max_dimension:
                    if original_width > original_height:
                        new_width = max_dimension
                        new_height = int(original_height * (max_dimension / original_width))
                    else:
                        new_height = max_dimension
                        new_width = int(original_width * (max_dimension / original_height))
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Apply slight enhancement
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.1)
                
                # Save with optimized settings
                output_path = self._get_output_path(input_path, "optimized")
                img.save(output_path, 'JPEG', quality=85, optimize=True, progressive=True)
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
    
    def _convert_format(self, input_path: str, output_format: str) -> Optional[str]:
        """Convert image to specified format."""
        try:
            with Image.open(input_path) as img:
                # Handle different format requirements
                if output_format.upper() == 'JPEG':
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for JPEG
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                
                elif output_format.upper() == 'PNG':
                    if img.mode not in ('RGB', 'RGBA', 'L', 'LA'):
                        img = img.convert('RGBA')
                
                elif output_format.upper() == 'WEBP':
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_converted.{output_format.lower()}"
                )
                
                # Save with format-specific settings
                if output_format.upper() == 'JPEG':
                    img.save(output_path, 'JPEG', quality=95, optimize=True)
                elif output_format.upper() == 'PNG':
                    img.save(output_path, 'PNG', optimize=True)
                elif output_format.upper() == 'WEBP':
                    img.save(output_path, 'WebP', quality=95, optimize=True)
                else:
                    img.save(output_path, output_format.upper())
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error converting format: {e}")
            return None
    
    def _simple_resize(self, input_path: str, target_size: Tuple[int, int], suffix: str) -> Optional[str]:
        """Simple resize using PIL as fallback."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize using high-quality resampling
                resized = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Apply slight sharpening
                enhancer = ImageEnhance.Sharpness(resized)
                sharpened = enhancer.enhance(1.2)
                
                # Save processed image
                output_path = self._get_output_path(input_path, suffix)
                sharpened.save(output_path, 'JPEG', quality=95, optimize=True)
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error in simple resize: {e}")
            return None
    
    def _smart_resize(self, input_path: str, target_size: Tuple[int, int], suffix: str) -> Optional[str]:
        """Smart resize for images that are already large enough."""
        try:
            with Image.open(input_path) as img:
                original_width, original_height = img.size
                target_width, target_height = target_size
                
                # Calculate aspect ratios
                original_ratio = original_width / original_height
                target_ratio = target_width / target_height
                
                if abs(original_ratio - target_ratio) < 0.01:
                    # Aspect ratios match, direct resize
                    resized = img.resize(target_size, Image.Resampling.LANCZOS)
                else:
                    # Crop to maintain aspect ratio, then resize
                    if original_ratio > target_ratio:
                        # Original is wider
                        new_width = int(original_height * target_ratio)
                        left = (original_width - new_width) // 2
                        img = img.crop((left, 0, left + new_width, original_height))
                    else:
                        # Original is taller
                        new_height = int(original_width / target_ratio)
                        top = (original_height - new_height) // 2
                        img = img.crop((0, top, original_width, top + new_height))
                    
                    resized = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Apply enhancement
                enhancer = ImageEnhance.Sharpness(resized)
                enhanced = enhancer.enhance(1.1)
                
                # Save processed image
                output_path = self._get_output_path(input_path, suffix)
                enhanced.save(output_path, 'JPEG', quality=95, optimize=True)
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error in smart resize: {e}")
            return None
    
    def _custom_upscale(self, input_path: str, scale_factor: int, mode: str = "standard") -> Optional[str]:
        """Custom upscale implementation with different modes."""
        try:
            logger.info(f"Starting custom upscale: {scale_factor}x, mode: {mode}")
            
            # Load image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    # For upscaling, preserve transparency by converting to RGBA
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                logger.info(f"Original dimensions: {original_width}x{original_height}")
                
                # Calculate new dimensions
                new_width = original_width * scale_factor
                new_height = original_height * scale_factor
                
                logger.info(f"Target dimensions: {new_width}x{new_height}")
                
                # Different upscaling modes
                if mode == "smart":
                    upscaled = self._smart_upscale_image(img, (new_width, new_height))
                elif mode == "max":
                    upscaled = self._max_quality_upscale_image(img, (new_width, new_height))
                else:  # standard mode
                    upscaled = self._standard_upscale_image(img, (new_width, new_height))
                
                # Save result
                output_path = self._get_output_path(input_path, f"{scale_factor}x_{mode}")
                
                # Save with appropriate format and quality
                if upscaled.mode == 'RGBA':
                    output_path = output_path.replace('.jpg', '.png')
                    upscaled.save(output_path, 'PNG', optimize=True)
                else:
                    upscaled.save(output_path, 'JPEG', quality=95, optimize=True, progressive=True)
                
                logger.info(f"Custom upscale completed: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error in custom upscale: {e}")
            return None
    
    def _standard_upscale_image(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Standard upscaling with LANCZOS resampling."""
        return img.resize(target_size, Image.Resampling.LANCZOS)
    
    def _smart_upscale_image(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Smart upscaling with progressive scaling and enhancement."""
        original_size = img.size
        target_width, target_height = target_size
        
        # Calculate scale factor
        scale_x = target_width / original_size[0]
        scale_y = target_height / original_size[1]
        max_scale = max(scale_x, scale_y)
        
        current_img = img
        
        # Progressive upscaling for large scale factors
        if max_scale > 4.0:
            # Scale in steps to maintain quality
            steps = int(np.log2(max_scale)) + 1
            for step in range(steps):
                if step == steps - 1:
                    # Final step to exact target size
                    intermediate_size = target_size
                else:
                    # Intermediate steps - double the size
                    current_scale = 2 ** (step + 1)
                    intermediate_size = (
                        min(int(original_size[0] * current_scale), target_width),
                        min(int(original_size[1] * current_scale), target_height)
                    )
                
                # Upscale with high-quality resampling
                current_img = current_img.resize(intermediate_size, Image.Resampling.LANCZOS)
                
                # Apply enhancement after each step
                if step < steps - 1:  # Don't enhance the final image too much
                    enhancer = ImageEnhance.Sharpness(current_img)
                    current_img = enhancer.enhance(1.05)
        else:
            # Single-step upscaling for smaller scale factors
            current_img = current_img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Final enhancement
        enhancer = ImageEnhance.Sharpness(current_img)
        current_img = enhancer.enhance(1.1)
        
        return current_img
    
    def _max_quality_upscale_image(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Maximum quality upscaling with OpenCV processing."""
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(img)
            
            # Handle different image modes
            if img.mode == 'RGB':
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            elif img.mode == 'RGBA':
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
            else:
                # Fallback to smart method
                return self._smart_upscale_image(img, target_size)
            
            # Apply noise reduction
            img_cv = cv2.bilateralFilter(img_cv, 9, 75, 75)
            
            # Use INTER_CUBIC for high-quality upscaling
            upscaled_cv = cv2.resize(img_cv, target_size, interpolation=cv2.INTER_CUBIC)
            
            # Apply unsharp masking for enhanced details
            gaussian = cv2.GaussianBlur(upscaled_cv, (0, 0), 2.0)
            upscaled_cv = cv2.addWeighted(upscaled_cv, 1.5, gaussian, -0.5, 0)
            
            # Convert back to PIL
            if img.mode == 'RGB':
                final_array = cv2.cvtColor(upscaled_cv, cv2.COLOR_BGR2RGB)
            elif img.mode == 'RGBA':
                final_array = cv2.cvtColor(upscaled_cv, cv2.COLOR_BGRA2RGBA)
            else:
                final_array = upscaled_cv
            
            return Image.fromarray(final_array.astype('uint8'))
            
        except Exception as e:
            logger.warning(f"OpenCV upscaling failed, falling back to smart upscale: {e}")
            return self._smart_upscale_image(img, target_size)

    def _get_output_path(self, input_path: str, suffix: str) -> str:
        """Generate output path for processed image."""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(self.temp_dir, f"{base_name}_{suffix}.jpg")
