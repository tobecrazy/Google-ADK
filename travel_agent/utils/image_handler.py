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
    
    def get_attraction_images(self, destination: str, attractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get images for attractions using free image services.
        
        Args:
            destination: Destination name
            attractions: List of attraction data
            
        Returns:
            List of attractions with image URLs
        """
        try:
            enhanced_attractions = []
            
            for attraction in attractions:
                try:
                    attraction_name = attraction.get('name', '')
                    
                    # Generate search terms for images
                    search_terms = [
                        f"{destination} {attraction_name}",
                        f"{attraction_name} {destination}",
                        f"{destination} landmark",
                        f"{destination} tourist attraction"
                    ]
                    
                    # Try to get image URL from Unsplash
                    image_url = self._get_unsplash_image(search_terms[0])
                    
                    if not image_url:
                        # Fallback to other search terms
                        for term in search_terms[1:]:
                            image_url = self._get_unsplash_image(term)
                            if image_url:
                                break
                    
                    # Add image URL to attraction data
                    enhanced_attraction = attraction.copy()
                    enhanced_attraction['image_url'] = image_url
                    enhanced_attraction['has_image'] = bool(image_url)
                    
                    enhanced_attractions.append(enhanced_attraction)
                    
                except Exception as e:
                    logger.error(f"Error getting image for attraction {attraction.get('name', 'Unknown')}: {str(e)}")
                    enhanced_attraction = attraction.copy()
                    enhanced_attraction['image_url'] = None
                    enhanced_attraction['has_image'] = False
                    enhanced_attractions.append(enhanced_attraction)
            
            return enhanced_attractions
            
        except Exception as e:
            logger.error(f"Error getting attraction images: {str(e)}")
            return attractions
    
    def _get_unsplash_image(self, search_term: str) -> Optional[str]:
        """
        Get image URL from multiple image sources with fallback.
        
        Args:
            search_term: Search term for image
            
        Returns:
            Image URL or None
        """
        try:
            # Try multiple image sources
            image_sources = [
                self._try_unsplash_source(search_term),
                self._try_picsum_image(search_term),
                self._try_placeholder_image(search_term)
            ]
            
            for image_url in image_sources:
                if image_url:
                    logger.info(f"Found image for '{search_term}': {image_url}")
                    return image_url
            
            logger.warning(f"No image found for '{search_term}', using placeholder")
            return self._generate_placeholder_url(search_term)
            
        except Exception as e:
            logger.error(f"Error getting image for '{search_term}': {str(e)}")
            return self._generate_placeholder_url(search_term)
    
    def _try_unsplash_source(self, search_term: str) -> Optional[str]:
        """Try to get image from Unsplash Source API."""
        try:
            # Clean search term for better results
            clean_term = self._clean_search_term(search_term)
            base_url = "https://source.unsplash.com/800x600"
            search_url = f"{base_url}/?{clean_term}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.head(search_url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return search_url
            
            return None
            
        except Exception as e:
            logger.debug(f"Unsplash source failed for '{search_term}': {str(e)}")
            return None
    
    def _try_picsum_image(self, search_term: str) -> Optional[str]:
        """Try to get a random image from Picsum (Lorem Picsum)."""
        try:
            # Generate a seed based on search term for consistent images
            import hashlib
            seed = abs(hash(search_term)) % 1000
            picsum_url = f"https://picsum.photos/seed/{seed}/800/600"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(picsum_url, headers=headers, timeout=5)
            if response.status_code == 200:
                return picsum_url
            
            return None
            
        except Exception as e:
            logger.debug(f"Picsum failed for '{search_term}': {str(e)}")
            return None
    
    def _try_placeholder_image(self, search_term: str) -> Optional[str]:
        """Try to get image from placeholder services."""
        try:
            # Use placeholder.com service
            clean_term = self._clean_search_term(search_term)
            placeholder_url = f"https://via.placeholder.com/800x600/4A90E2/FFFFFF?text={clean_term.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(placeholder_url, headers=headers, timeout=5)
            if response.status_code == 200:
                return placeholder_url
            
            return None
            
        except Exception as e:
            logger.debug(f"Placeholder service failed for '{search_term}': {str(e)}")
            return None
    
    def _clean_search_term(self, search_term: str) -> str:
        """Clean search term for better image search results."""
        try:
            # Remove common words that don't help with image search
            stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            
            # Split and clean
            words = search_term.lower().split()
            cleaned_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Take first 3 most relevant words
            cleaned_term = ' '.join(cleaned_words[:3])
            
            # URL encode
            import urllib.parse
            return urllib.parse.quote_plus(cleaned_term)
            
        except Exception as e:
            logger.debug(f"Error cleaning search term '{search_term}': {str(e)}")
            import urllib.parse
            return urllib.parse.quote_plus(search_term)
    
    def _generate_placeholder_url(self, search_term: str) -> str:
        """Generate a placeholder image URL as fallback."""
        try:
            # Create a more descriptive placeholder with text
            clean_term = search_term.replace(' ', '+')[:30]  # Limit length
            colors = ['4A90E2', '50C878', 'FF6B6B', 'FFD93D', '6C5CE7', 'A29BFE']
            
            # Choose color based on search term hash
            color_index = abs(hash(search_term)) % len(colors)
            bg_color = colors[color_index]
            
            # Add an emoji based on the type of place
            emoji = "📷"
            if any(word in search_term.lower() for word in ['海洋', '水族', 'aquarium', '海洋馆']):
                emoji = "🐋"
            elif any(word in search_term.lower() for word in ['公园', 'park']):
                emoji = "🌳"
            elif any(word in search_term.lower() for word in ['博物馆', 'museum']):
                emoji = "🏛️"
            elif any(word in search_term.lower() for word in ['餐厅', 'restaurant']):
                emoji = "🍽️"
            elif any(word in search_term.lower() for word in ['寺庙', 'temple']):
                emoji = "🛕"
            
            return f"https://via.placeholder.com/800x600/{bg_color}/FFFFFF?text={emoji}+{clean_term}"
            
        except Exception as e:
            logger.error(f"Error generating placeholder URL: {str(e)}")
            return "https://via.placeholder.com/800x600/CCCCCC/FFFFFF?text=📷+No+Image"
    
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
            # Create a simple placeholder image with gradient background
            image = Image.new('RGB', (width, height), color='#f0f0f0')
            
            # Convert to base64
            return self.image_to_base64(image, format='JPEG', quality=70)
            
        except Exception as e:
            logger.error(f"Error creating placeholder image: {str(e)}")
            # Return a better SVG placeholder with more descriptive text
            import urllib.parse
            encoded_text = urllib.parse.quote_plus(text[:30])  # Limit text length
            svg_placeholder = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#f5f5f5;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <rect width="100%" height="100%" fill="url(#grad)" />
                <text x="50%" y="40%" font-family="Arial, sans-serif" font-size="24" fill="#666" text-anchor="middle">No Image</text>
                <text x="50%" y="60%" font-family="Arial, sans-serif" font-size="16" fill="#999" text-anchor="middle">{encoded_text}</text>
                <text x="50%" y="80%" font-family="Arial, sans-serif" font-size="40" fill="#ccc" text-anchor="middle">📷</text>
            </svg>'''
            import base64
            return f"data:image/svg+xml;base64,{base64.b64encode(svg_placeholder.encode('utf-8')).decode('utf-8')}"
