import logging

from config import TELEGRAM_GROUP_CHAT_ID
from docx import Document

logger = logging.getLogger(__name__)



document = Document('шаблон.docx')













# def send_document_to_user(message, bot):
    #
    # bot.send_document(chat_id=TELEGRAM_GROUP_CHAT_ID, document=message.document.file_id,
    #                   caption=f'Резюме от пользователя:\n{message.from_user.first_name}',
    #                   disable_content_type_detection=True)
    # bot.delete_state(message.from_user.id, message.chat.id)
    # bot.send_message(message.chat.id, f'Резюме получено!', )
    # logger.info(f'State пользователя удалён -- {bot.get_state(message.from_user.id, message.chat.id)}')
