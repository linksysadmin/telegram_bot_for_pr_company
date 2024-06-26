import logging

logging.getLogger(__name__)

TEXT_MESSAGES = {
    'start': "Ваш профиль 🧑‍💻\n"
             "Имя: <b>{username}</b>\n"
             "Компания: <b>{company}</b>\n",
    'start_unauthorized': 'Здравствуйте! Вас приветствует 🤖 компании <b>Mr.Эйч</b> ©️\n\n'
                          'Для использования бота вам нужно зарегистрироваться, введите пожалуйста ваше имя\n\n',
    'start_for_operator': 'Личный кабинет оператора 🧑‍💻',
    'start_for_partners': 'Личный кабинет партнера компании Mr.Эйч',
    'info': "info",
    'chat_with_operator': 'Перейти в диалог: @mrh_agency',
    'menu': 'Выберите: ',
    'scenario': 'Сценарий:',
    'caption_for_technical_tasks': 'Техническое задание от пользователя:\n{name}\n'
                                   'Username: {tg_username}\n'
                                   'Компания: {company]}\n'
                                   'Телефон: {phone}\n'
                                   'Website: {website}\n',
    'visible_file_name_for_technical_tasks': 'Тех.задание компании {company}.docx'
}
