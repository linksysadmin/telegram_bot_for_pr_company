import logging


logger = logging.getLogger(__name__)


def callback_for_enter_menu(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    match call.data:
        case 'requests':
            bot.send_message(call.message.chat.id, 'Здесь отображаются все запросы от пользователей')
        case 'clients':
            bot.send_message(call.message.chat.id, 'Здесь отображаются все чаты с пользователями, с которыми ведется переписка')
        case 'tasks':
            bot.send_message(call.message.chat.id, 'Здесь отображаются все чаты со сформированной задачей от пользователя, которую запускают в продакшн')
        case 'settings':
            bot.send_message(call.message.chat.id, 'Здесь будет сценарий, при котором можно будет самостоятельно менять вопросы брифа')

