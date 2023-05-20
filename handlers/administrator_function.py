from config import PASSWORD_FOR_ADMIN
from services.send_info_to_database import add_admin_to_db


def check_password_and_add_admin_to_db(message, bot):
    if message.text == PASSWORD_FOR_ADMIN:
        add_admin_to_db(message.from_user.id)
        bot.send_message(message.chat.id, f'Пароль введен верно, нажмите /get_excel')
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.chat.id, f'Пароль введен неверно')
