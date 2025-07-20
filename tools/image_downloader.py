from crewai.tools.base_tool import BaseTool
import requests
import os
from urllib.parse import urlparse
import time
from typing import Optional
import mimetypes

def is_valid_image_url(url: str) -> bool:
    """
    Check if a URL is likely to be a direct image URL.
    """
    # List of domains that typically serve HTML pages instead of images
    html_domains = {
        'instagram.com', 'facebook.com', 'twitter.com', 'x.com', 
        'linkedin.com', 'pinterest.com', 'tiktok.com', 'youtube.com'
    }
    
    # List of common image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'}
    
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Check if it's a social media domain
    if any(social_domain in domain for social_domain in html_domains):
        return False
    
    # Check if URL has image extension
    path = parsed.path.lower()
    if any(ext in path for ext in image_extensions):
        return True
    
    # Check if URL contains image-related paths
    image_paths = ['/image/', '/img/', '/photo/', '/picture/', '/media/']
    if any(img_path in path for img_path in image_paths):
        return True
    
    return False

def download_mood_board_image(image_url: str, save_path: str):
    """
    Downloads an image from a URL and saves it to the specified mood board folder.
    Returns a success or error message.
    """
    try:
        # Validate URL first
        if not is_valid_image_url(image_url):
            return f"❌ Invalid image URL: {image_url}\nThis appears to be a social media page URL, not a direct image URL. Please search for actual image URLs (ending in .jpg, .png, etc.) or use stock photo sites."
        
        # Create mood board directory
        os.makedirs(save_path, exist_ok=True)
        
        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if response is actually an image
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return f"❌ URL does not return an image: {image_url}\nContent-Type: {content_type}\nThis appears to be an HTML page, not an image. Please use direct image URLs."
        
        # Generate filename from URL
        path = urlparse(image_url).path.rstrip('/')  # Remove trailing slashes
        filename = os.path.basename(path)
        
        # If filename is empty or looks like a directory, generate a fallback
        if not filename or '.' not in filename or filename.endswith('.'):
            # Try to get extension from content-type
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # default
            filename = f"mood_image_{int(time.time())}{ext}"
        
        filepath = os.path.join(save_path, filename)
        
        # Ensure we never create a directory by mistake
        if os.path.isdir(filepath):
            # If a directory exists with this name, add a suffix
            filename = f"{filename}_img"
            filepath = os.path.join(save_path, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return f"✅ Image downloaded successfully to {filepath}"
    except requests.exceptions.RequestException as e:
        return f"❌ Failed to download image from {image_url}: Network error - {str(e)}"
    except Exception as e:
        return f"❌ Failed to download image from {image_url}: {str(e)}"

class MoodBoardImageTool(BaseTool):
    name: str = "MoodBoardImageTool"
    description: str = "Downloads images from URLs and saves them to a mood board folder for video production. IMPORTANT: Only use direct image URLs (ending in .jpg, .png, etc.) or stock photo URLs. Do NOT use social media URLs like Instagram, Facebook, etc. as they will not work."
    
    def _run(self, image_url: str, save_path: str) -> str:
        return download_mood_board_image(image_url, save_path) 