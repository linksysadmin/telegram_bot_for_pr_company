import logging

logging.getLogger(__name__)

TEXT_MESSAGES = {
    'start': "Ваш профиль 🧑‍💻\n"
             "Имя: <b>{username}</b>\n"
             "Компания: <b>{company}</b>\n",
    'start_unauthorized': 'Здравствуйте! Вас приветствует 🤖 компании <b>Mr.Эйч</b>\n'
                          'Пройдите пожалуйста процесс регистрации\n\nВведите ваше имя:',
    'start_for_operator': 'Личный кабинет оператора 🧑‍💻',
    'info': "info",
    'chat_with_operator': 'Перейти в диалог: @mrh_agency',
    'menu': 'Выберите: ',
    'scenario': 'Сценарий:',
}
