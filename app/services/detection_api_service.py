import requests
from app.config import settings


class DetectionAPIService:
    """Service for handling Detection API operations."""

    def __init__(self):
        self.base_url = settings.DETECTION_API_URL.rstrip('/')

    def process_image(self, image_url: str, result_id: int) -> dict:
        """
        Send an image URL to the Detection API for processing.
        
        Args:
            image_url: The GCP Cloud Storage URL of the image
            result_id: The ID of the result record
            
        Returns:
            The API response as a dictionary
            
        Raises:
            Exception: If the API call fails
        """
        try:
            endpoint = f"{self.base_url}/process-images"
            payload = {
                "image_url": image_url,
                "resultId": result_id
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            # Return the JSON response
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("Detection API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call Detection API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing image with Detection API: {str(e)}")

