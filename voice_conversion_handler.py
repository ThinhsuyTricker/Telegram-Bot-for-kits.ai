import requests
import logging
from telegram import Update, Audio
from telegram.ext import ContextTypes, ConversationHandler
from api_manager import APIManager

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Định nghĩa các trạng thái của cuộc hội thoại
GET_MODEL_ID, GET_AUDIO_FILE = range(2)

class VoiceConversionHandler:
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager

    async def start_conversion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Vui lòng nhập voiceModelId để bắt đầu:")
        return GET_MODEL_ID

    async def get_model_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['voice_model_id'] = update.message.text
        await update.message.reply_text("Vui lòng gửi file âm thanh (wav, webm, mp3, flac):")
        return GET_AUDIO_FILE

    async def get_audio_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        api_key = self.api_manager.get_user_api_key(user_id)
        
        if not api_key:
            await update.message.reply_text("API key không tồn tại. Vui lòng sử dụng /add_api để thêm API key của bạn.")
            return ConversationHandler.END

        # Validate API key
        if not self.api_manager.validate_api_key(api_key):
            await update.message.reply_text("API key không hợp lệ. Vui lòng sử dụng /add_api để thêm API key hợp lệ.")
            return ConversationHandler.END

        # Kiểm tra và lấy file_id từ các loại tệp được gửi
        if update.message.voice:
            file_id = update.message.voice.file_id
        elif update.message.audio:
            file_id = update.message.audio.file_id
        elif update.message.document and update.message.document.mime_type in ['audio/wav', 'audio/webm', 'audio/mp3', 'audio/flac']:
            file_id = update.message.document.file_id
        else:
            await update.message.reply_text("File không hợp lệ. Vui lòng gửi lại file âm thanh (wav, webm, mp3, flac):")
            return GET_AUDIO_FILE

        # Tải tệp về
        file = await context.bot.get_file(file_id)
        file_data = await file.download_as_bytearray()
        file_name = file.file_path.split('/')[-1]

        # Lưu tạm thời tệp đã tải xuống
        with open(file_name, "wb") as f:
            f.write(file_data)

        # Thực hiện gọi API chuyển đổi giọng nói
        url = "https://arpeggi.io/api/kits/v1/voice-conversions"
        files = {
            "soundFile": (file_name, open(file_name, "rb"))  # Tạo tệp gửi dưới dạng byte array với tên tệp
        }
        data = {
            "voiceModelId": context.user_data['voice_model_id']
        }
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            logger.info(f"API Response: {response.text}")
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'completed':
                    await update.message.reply_text(f"Chuyển đổi thành công! Tải xuống tệp tại: {result['outputFileUrl']}")
                else:
                    await update.message.reply_text("Quá trình chuyển đổi đang chạy. Vui lòng kiểm tra sau.")
            else:
                await update.message.reply_text("Có lỗi xảy ra khi thực hiện chuyển đổi giọng nói.")
        except Exception as e:
            logger.error(f"Error during voice conversion: {e}")
            await update.message.reply_text("Có lỗi xảy ra khi thực hiện chuyển đổi giọng nói.")
        finally:
            files["soundFile"][1].close()  # Đóng tệp sau khi gửi

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Đã hủy bỏ quá trình.")
        return ConversationHandler.END
