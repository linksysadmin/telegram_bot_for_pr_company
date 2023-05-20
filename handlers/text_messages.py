import logging

logging.getLogger(__name__)

TEXT_MESSAGES = {
    'start': "Ваш профиль 🧑‍💻\n"
             "Имя: <b>{username}</b>\n"
             "Компания: <b>{company}</b>\n",

    'start_unauthorized': 'Здравствуйте! Вас приветствует 🤖 компании <b>Mr.Эйч</b>\n'
                          'Пройдите пожалуйста процесс регистрации\n\nВведите ваше имя:',
    'info': "info",
    'chat_with_operator': 'Связаться с оператором: @mrh_agency',
    'menu': 'Выберите: ',
    'scenario': 'Сценарий:',
}
