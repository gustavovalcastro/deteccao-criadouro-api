import uuid
from azure.storage.blob import BlobServiceClient
from app.config import settings


class AzureStorageService:
    """Service for handling Azure Blob Storage operations."""

    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self._ensure_container_exists()

    def _ensure_container_exists(self):
        """Ensure the container exists, create it if it doesn't."""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            raise Exception(f"Failed to ensure container exists: {str(e)}")

    def upload_image(self, image_data: bytes, file_extension: str = "jpg") -> str:
        """
        Upload an image to Azure Blob Storage.
        
        Args:
            image_data: The image file data as bytes
            file_extension: File extension (default: jpg)
            
        Returns:
            The URL of the uploaded blob
        """
        try:
            # Generate unique blob name
            blob_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload the image
            blob_client.upload_blob(image_data, overwrite=True)
            
            # Return the blob URL
            return blob_client.url
            
        except Exception as e:
            raise Exception(f"Failed to upload image to Azure Storage: {str(e)}")

