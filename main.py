from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from config import Config
from api_manager import APIManager
from add_api import AddAPI
from voice_conversion_handler import VoiceConversionHandler, GET_MODEL_ID, GET_AUDIO_FILE

def main():
    # Khởi tạo các đối tượng cần thiết
    api_manager = APIManager()
    add_api_handler = AddAPI(api_manager)
    voice_conversion_handler = VoiceConversionHandler(api_manager)

    application = Application.builder().token(Config.TOKEN).build()

    # Đăng ký các lệnh của bot
    application.add_handler(CommandHandler('add_api', add_api_handler.add_api_key))

    # Thiết lập ConversationHandler cho lệnh /convert
    convert_handler = ConversationHandler(
        entry_points=[CommandHandler('convert', voice_conversion_handler.start_conversion)],
        states={
            GET_MODEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, voice_conversion_handler.get_model_id)],
            GET_AUDIO_FILE: [MessageHandler(filters.VOICE | filters.AUDIO | filters.Document.AUDIO, voice_conversion_handler.get_audio_file)]
        },
        fallbacks=[CommandHandler('cancel', voice_conversion_handler.cancel)],
    )

    # Đăng ký handler cho lệnh /convert
    application.add_handler(convert_handler)

    # Bắt đầu bot
    application.run_polling()

if __name__ == '__main__':
    main()
