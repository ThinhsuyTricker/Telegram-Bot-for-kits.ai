from database import get_session, User
import logging
import requests

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self):
        self.session = get_session()

    def get_user_api_key(self, user_id):
        try:
            user = self.session.query(User).filter_by(userid=user_id).first()
            if user:
                logger.info(f"API key for user {user_id} found: {user.api_key}")
                return user.api_key
            else:
                logger.warning(f"API key for user {user_id} not found.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving API key for user {user_id}: {e}")
            return None

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validates the API key by making a test request to the Kits.ai API.
        Returns True if the API key is valid, False otherwise.
        """
        url = "https://arpeggi.io/api/kits/v1/voice-conversions"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(url, headers=headers)
            # Check if the response is successful
            if response.status_code == 200:
                return True
            elif response.status_code == 403:
                # Handle specific error response
                error_message = response.json().get("message", "")
                if error_message == "Invalid api key format":
                    return False
        except requests.RequestException as e:
            logger.error(f"Error validating API key: {e}")
            return False

        return False
