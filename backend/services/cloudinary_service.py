"""Cloudinary Image Upload Service"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from typing import Dict, Optional
import uuid


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
    
    def upload_from_url(self, image_url: str, folder: str = "poddb", public_id: Optional[str] = None) -> Dict:
        """
        Upload image from URL to Cloudinary
        
        Args:
            image_url: URL of the image to upload
            folder: Cloudinary folder name (default: poddb)
            public_id: Optional custom public ID
        
        Returns:
            Dict with url, secure_url, public_id
        """
        try:
            if not public_id:
                public_id = f"{folder}_{uuid.uuid4().hex[:12]}"
            
            result = cloudinary.uploader.upload(
                image_url,
                folder=folder,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            
            return {
                'url': result['url'],
                'secure_url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result['width'],
                'height': result['height']
            }
        except Exception as e:
            raise Exception(f"Cloudinary upload error: {str(e)}")
    
    def upload_from_file(self, file_path: str, folder: str = "poddb", public_id: Optional[str] = None) -> Dict:
        """
        Upload image from local file to Cloudinary
        
        Args:
            file_path: Path to local file
            folder: Cloudinary folder name
            public_id: Optional custom public ID
        
        Returns:
            Dict with url, secure_url, public_id
        """
        try:
            if not public_id:
                public_id = f"{folder}_{uuid.uuid4().hex[:12]}"
            
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            
            return {
                'url': result['url'],
                'secure_url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result['width'],
                'height': result['height']
            }
        except Exception as e:
            raise Exception(f"Cloudinary upload error: {str(e)}")
    
    def upload_base64(self, base64_string: str, folder: str = "poddb", public_id: Optional[str] = None) -> Dict:
        """
        Upload base64 encoded image to Cloudinary
        
        Args:
            base64_string: Base64 encoded image string
            folder: Cloudinary folder name
            public_id: Optional custom public ID
        
        Returns:
            Dict with url, secure_url, public_id
        """
        try:
            if not public_id:
                public_id = f"{folder}_{uuid.uuid4().hex[:12]}"
            
            result = cloudinary.uploader.upload(
                base64_string,
                folder=folder,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            
            return {
                'url': result['url'],
                'secure_url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result['width'],
                'height': result['height']
            }
        except Exception as e:
            raise Exception(f"Cloudinary upload error: {str(e)}")
    
    def delete_image(self, public_id: str) -> bool:
        """Delete image from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    def download_and_upload_youtube_thumbnail(self, youtube_thumbnail_url: str, identifier: str, folder: str = "episodes") -> Dict:
        """
        Download YouTube thumbnail and upload to Cloudinary
        
        Args:
            youtube_thumbnail_url: YouTube thumbnail URL
            identifier: Unique identifier for the image (e.g., video_id)
            folder: Cloudinary folder
        
        Returns:
            Dict with Cloudinary image details
        """
        try:
            # YouTube thumbnails are already publicly accessible, so we can directly upload
            public_id = f"{identifier}"
            return self.upload_from_url(youtube_thumbnail_url, folder=folder, public_id=public_id)
        except Exception as e:
            raise Exception(f"Error uploading YouTube thumbnail: {str(e)}")


# Singleton instance
cloudinary_service = CloudinaryService()
