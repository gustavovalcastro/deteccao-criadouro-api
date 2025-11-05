import uuid
import os
from google.cloud import storage
from google.oauth2 import service_account
from google.auth import exceptions as auth_exceptions
from app.config import settings


class GCPStorageService:
    """Service for handling Google Cloud Storage operations."""

    def __init__(self):
        try:
            # If credentials path is specified in settings, use it
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Set environment variable for Google Cloud library
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
                # Also verify file exists
                if not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                    raise Exception(
                        f"GCP credentials file not found at: {settings.GOOGLE_APPLICATION_CREDENTIALS}"
                    )
                # Initialize client with explicit credentials
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                self.client = storage.Client(credentials=credentials)
            else:
                # Try to use environment variable or Application Default Credentials
                creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if creds_path and not os.path.exists(creds_path):
                    raise Exception(f"GCP credentials file not found at: {creds_path}")
                # Initialize the storage client (will use GOOGLE_APPLICATION_CREDENTIALS if set)
                self.client = storage.Client()
        except auth_exceptions.DefaultCredentialsError as e:
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'not set')
            settings_path = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
            raise Exception(
                f"GCP credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS in your .env file "
                f"or as an environment variable to point to your service account key file. "
                f"Current env var: {creds_path}. Current setting: {settings_path}. "
                f"Original error: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize GCP Storage client: {str(e)}")
        
        self.bucket_name = settings.GCP_STORAGE_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create it if it doesn't."""
        try:
            bucket = self.client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket.create()
        except Exception as e:
            raise Exception(f"Failed to ensure bucket exists: {str(e)}")

    def upload_image(self, image_data: bytes, file_extension: str = "jpg") -> str:
        """
        Upload an image to Google Cloud Storage.
        
        Args:
            image_data: The image file data as bytes
            file_extension: File extension (default: jpg)
            
        Returns:
            The public URL of the uploaded blob
        """
        try:
            # Generate unique blob name
            blob_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Get bucket and blob
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            
            # Upload the image
            blob.upload_from_string(image_data, content_type=f"image/{file_extension}")
            
            # Make blob publicly accessible (optional, adjust based on your needs)
            # blob.make_public()
            
            # Return the blob URL
            # Use public_url if available, otherwise construct gs:// URL or https URL
            if blob.public_url:
                return blob.public_url
            else:
                # Construct the public URL format: https://storage.googleapis.com/{bucket}/{blob_name}
                return f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
            
        except Exception as e:
            raise Exception(f"Failed to upload image to GCP Storage: {str(e)}")

