# add_api.py
import requests
from telegram import Update
from telegram.ext import CallbackContext
from api_manager import APIManager
from database import User, get_session
from sqlalchemy.exc import SQLAlchemyError

class AddAPI:
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager

    async def add_api_key(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        username = update.effective_user.username or "unknown"

        if len(context.args) != 1:
            await update.message.reply_text("Vui lòng cung cấp API key của bạn sau lệnh /add_api.")
            return

        api_key = context.args[0]

        # Validate API key
        if not self.validate_api_key(api_key):
            await update.message.reply_text("API key không hợp lệ hoặc có định dạng không đúng.")
            return

        # Add or update user API key in the database
        with get_session() as session:
            try:
                user = session.query(User).filter_by(userid=user_id).first()
                if user:
                    user.api_key = api_key
                    await update.message.reply_text("API key đã được cập nhật thành công.")
                else:
                    user = User(username=username, userid=user_id, api_key=api_key)
                    session.add(user)
                    await update.message.reply_text("API key đã được thêm thành công.")

                # Commit the transaction
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                await update.message.reply_text(f"Đã xảy ra lỗi khi lưu API key: {str(e)}")

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
            print(f"Error validating API key: {e}")
            return False

        return False
