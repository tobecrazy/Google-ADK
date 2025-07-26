"""
Image Handler Utility
Handles image processing and optimization for travel reports
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageOps
import requests
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class ImageHandler:
    """Utility for image processing and optimization."""
    
    def __init__(self):
        """Initialize the image handler."""
        self.supported_formats = ['JPEG', 'PNG', 'WebP', 'GIF']
        self.max_size = (1200, 800)  # Max dimensions for web display
        self.thumbnail_size = (300, 200)  # Thumbnail dimensions
        
        logger.info("Image Handler initialized")
    
    def download_image(self, url: str, timeout: int = 10) -> Optional[Image.Image]:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            timeout: Request timeout in seconds
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Check if content is an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL does not contain image content: {url}")
                return None
            
            # Open image from bytes
            image = Image.open(BytesIO(response.content))
            
            logger.info(f"Successfully downloaded image from {url}")
            return image
            
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None
    
    def optimize_image(
        self,
        image: Image.Image,
        max_size: Optional[Tuple[int, int]] = None,
        quality: int = 85,
        format: str = 'JPEG'
    ) -> Image.Image:
        """
        Optimize image for web display.
        
        Args:
            image: PIL Image object
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            format: Output format
            
        Returns:
            Optimized PIL Image object
        """
        try:
            if max_size is None:
                max_size = self.max_size
            
            # Convert to RGB if necessary (for JPEG)
            if format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if larger than max_size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Auto-orient based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            logger.info(f"Image optimized to {image.size}")
            return image
            
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            return image
    
    def create_thumbnail(self, image: Image.Image, size: Optional[Tuple[int, int]] = None) -> Image.Image:
        """
        Create thumbnail from image.
        
        Args:
            image: PIL Image object
            size: Thumbnail size (width, height)
            
        Returns:
            Thumbnail PIL Image object
        """
        try:
            if size is None:
                size = self.thumbnail_size
            
            # Create a copy to avoid modifying original
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            
            logger.info(f"Thumbnail created with size {thumbnail.size}")
            return thumbnail
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return image
    
    def save_image(
        self,
        image: Image.Image,
        filepath: str,
        format: str = 'JPEG',
        quality: int = 85
    ) -> bool:
        """
        Save image to file.
        
        Args:
            image: PIL Image object
            filepath: Output file path
            format: Image format
            quality: JPEG quality (1-100)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save with appropriate parameters
            if format == 'JPEG':
                image.save(filepath, format=format, quality=quality, optimize=True)
            else:
                image.save(filepath, format=format, optimize=True)
            
            logger.info(f"Image saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving image to {filepath}: {str(e)}")
            return False
    
    def image_to_base64(self, image: Image.Image, format: str = 'JPEG', quality: int = 85) -> str:
        """
        Convert image to base64 string for embedding in HTML.
        
        Args:
            image: PIL Image object
            format: Image format
            quality: JPEG quality (1-100)
            
        Returns:
            Base64 encoded image string
        """
        try:
            buffer = BytesIO()
            
            if format == 'JPEG':
                image.save(buffer, format=format, quality=quality, optimize=True)
            else:
                image.save(buffer, format=format, optimize=True)
            
            buffer.seek(0)
            image_data = buffer.getvalue()
            
            # Create data URL
            mime_type = f"image/{format.lower()}"
            base64_string = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:{mime_type};base64,{base64_string}"
            
            logger.info(f"Image converted to base64 ({len(base64_string)} characters)")
            return data_url
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            return ""
    
    def process_travel_images(
        self,
        image_urls: List[str],
        destination: str,
        output_dir: str
    ) -> List[Dict[str, Any]]:
        """
        Process multiple travel images for a destination.
        
        Args:
            image_urls: List of image URLs
            destination: Destination name for file naming
            output_dir: Output directory for processed images
            
        Returns:
            List of processed image information
        """
        try:
            processed_images = []
            
            for i, url in enumerate(image_urls[:10]):  # Limit to 10 images
                try:
                    # Download image
                    image = self.download_image(url)
                    if not image:
                        continue
                    
                    # Generate filenames
                    safe_destination = "".join(c for c in destination if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_destination = safe_destination.replace(' ', '_')
                    
                    main_filename = f"{safe_destination}_image_{i+1}.jpg"
                    thumb_filename = f"{safe_destination}_thumb_{i+1}.jpg"
                    
                    main_filepath = os.path.join(output_dir, main_filename)
                    thumb_filepath = os.path.join(output_dir, thumb_filename)
                    
                    # Optimize and save main image
                    optimized_image = self.optimize_image(image)
                    main_saved = self.save_image(optimized_image, main_filepath)
                    
                    # Create and save thumbnail
                    thumbnail = self.create_thumbnail(image)
                    thumb_saved = self.save_image(thumbnail, thumb_filepath)
                    
                    if main_saved and thumb_saved:
                        # Convert to base64 for HTML embedding
                        base64_main = self.image_to_base64(optimized_image)
                        base64_thumb = self.image_to_base64(thumbnail)
                        
                        processed_images.append({
                            'original_url': url,
                            'main_image': {
                                'filepath': main_filepath,
                                'filename': main_filename,
                                'size': optimized_image.size,
                                'base64': base64_main
                            },
                            'thumbnail': {
                                'filepath': thumb_filepath,
                                'filename': thumb_filename,
                                'size': thumbnail.size,
                                'base64': base64_thumb
                            },
                            'processed_successfully': True
                        })
                    
                except Exception as e:
                    logger.error(f"Error processing image {url}: {str(e)}")
                    processed_images.append({
                        'original_url': url,
                        'processed_successfully': False,
                        'error': str(e)
                    })
            
            logger.info(f"Processed {len(processed_images)} images for {destination}")
            return processed_images
            
        except Exception as e:
            logger.error(f"Error processing travel images: {str(e)}")
            return []
    
    def create_image_gallery_html(self, processed_images: List[Dict[str, Any]]) -> str:
        """
        Create HTML gallery from processed images.
        
        Args:
            processed_images: List of processed image data
            
        Returns:
            HTML string for image gallery
        """
        try:
            if not processed_images:
                return "<p>No images available</p>"
            
            gallery_html = '<div class="image-gallery">\n'
            
            for img_data in processed_images:
                if not img_data.get('processed_successfully'):
                    continue
                
                main_img = img_data.get('main_image', {})
                thumbnail = img_data.get('thumbnail', {})
                
                if main_img.get('base64') and thumbnail.get('base64'):
                    gallery_html += f'''
                    <div class="gallery-item">
                        <img src="{thumbnail['base64']}" 
                             alt="Travel Image" 
                             class="thumbnail"
                             onclick="showFullImage('{main_img['base64']}')"
                             style="cursor: pointer; width: {thumbnail['size'][0]}px; height: {thumbnail['size'][1]}px;">
                    </div>
                    '''
            
            gallery_html += '</div>\n'
            
            # Add JavaScript for full image display
            gallery_html += '''
            <script>
            function showFullImage(base64Data) {
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0,0,0,0.8); display: flex; justify-content: center;
                    align-items: center; z-index: 1000; cursor: pointer;
                `;
                
                const img = document.createElement('img');
                img.src = base64Data;
                img.style.cssText = 'max-width: 90%; max-height: 90%; object-fit: contain;';
                
                modal.appendChild(img);
                modal.onclick = () => document.body.removeChild(modal);
                document.body.appendChild(modal);
            }
            </script>
            '''
            
            return gallery_html
            
        except Exception as e:
            logger.error(f"Error creating image gallery HTML: {str(e)}")
            return "<p>Error creating image gallery</p>"
    
    def get_placeholder_image(self, width: int = 300, height: int = 200, text: str = "No Image") -> str:
        """
        Generate a placeholder image as base64 data URL.
        
        Args:
            width: Image width
            height: Image height
            text: Text to display on placeholder
            
        Returns:
            Base64 data URL for placeholder image
        """
        try:
            # Create a simple placeholder image
            image = Image.new('RGB', (width, height), color='#f0f0f0')
            
            # Convert to base64
            return self.image_to_base64(image, format='JPEG', quality=70)
            
        except Exception as e:
            logger.error(f"Error creating placeholder image: {str(e)}")
            return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg=="
