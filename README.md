# Telegram Bot for PR company (Mr.Эйч)


curl https://api.telegram.org/bot675567567:AAFenUQz3O2lDRпкууSZQPQiHYniYfDuc/setWebhook?url=https://1792-94-131-111-6.ngrok-free.app/675567567:AAFenUQz3O2lDRпкууSZQPQiHYniYfDuc/



### Задать и удалить команды:

    start = types.BotCommand('start', 'Меню')
    test = types.BotCommand('test', 'Тест')
    bot.set_my_commands([start, test])

или 

    bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("command1", "command1 description"),
            telebot.types.BotCommand("command2", "command2 description")
        ],    
    bot.delete_my_commands(scope=None, language_code=None)
    # check command
    cmd = bot.get_my_commands(scope=None, language_code=None)
    print([c.to_json() for c in cmd])

#### Создание топика 

    bot.create_forum_topic(TELEGRAM_GROUP_CHAT_ID, name='Эйч|Брифинг|@Направление')
    # отправляем сообщение с клавиатурой
    bot.send_message(
        chat_id=message.chat.id,
        text=f'тема создана'
    )

    chat_id = TELEGRAM_GROUP_CHAT_ID
    topic_text = 'Новый топик'
    topic_message = bot.send_message(chat_id, topic_text)


    print(chat_id[4:])
    # получаем ссылку на топик
    topic_link = f'https://t.me/c/{chat_id[4:]}/{topic_message.message_id - 1}'
    print(topic_link, topic_message, sep='\n')
    # отправляем ссылку на топик пользователю
    bot.send_message(message.chat.id, topic_link)



#### Диалог с оператором 


    def callback_instant_messaging_service(call, bot):
        # bot.delete_message(call.message.chat.id, call.message.id)
        REDIS.set(f'client_id_for_dialogue', call.from_user.id)
        bot.send_message(call.message.chat.id, 'Подождите пока оператор к вам присоединится...')
        bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {call.from_user.id}\n'
                                      f'Имя: {call.from_user.first_name}', reply_markup=keyboard_for_operator())
        bot.set_state(call.message.chat.id, MyStates.request, call.from_user.id)
        logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')
    
    
    def callback_enter_into_a_dialog(call, bot):
        try:
            client_id = int(REDIS.get(f'client_id_for_dialogue'))
            bot.set_state(client_id, MyStates.dialogue, client_id)
            bot.set_state(call.message.chat.id, MyStates.client, call.from_user.id)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(client_id, 'Вы вступили в диалог с оператором\n', reply_markup=keyboard_for_delete_dialogue())
            bot.send_message(call.message.chat.id, 'Вы вступили в диалог с клиентом\nНапишите ему:',
                             reply_markup=keyboard_for_delete_dialogue())
            logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')
        except Exception as e:
            logger.error(f'{e}')
            not_dialogs(call.from_user.id, bot)
    
    
    def send_request_to_operator(message, bot):
        REDIS.set(f'client_id_for_dialogue', message.from_user.id)
        bot.send_message(message.from_user.id, f'Подождите пожалуйста пока оператор к вам присоединиться...')
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')
    
    
    def send_message_to_client(message, bot):
        client_id = int(REDIS.get(f'client_id_for_dialogue'))
        bot.send_message(client_id, f'💬Сообщение от оператора:\n\n{message.text}',
                         reply_markup=keyboard_for_delete_dialogue())
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')
    
    
    def send_message_to_operator(message, bot):
        bot.send_message(OPERATOR_ID, f'💬Сообщение от клиента:\n{message.from_user.id}\n\n{message.text}',
                         reply_markup=keyboard_for_delete_dialogue())
    
    
    def callback_cancel_from_dialog(call, bot):
        try:
            bot.delete_message(call.message.chat.id, call.message.id)
            client_id = int(REDIS.get(f'client_id_for_dialogue'))
            bot.delete_state(OPERATOR_ID, OPERATOR_ID)
            bot.delete_state(client_id, client_id)
            logger.info(f'Состояние клиента - {bot.get_state(client_id, client_id)}')
            logger.info(f'Состояние оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
    
            if call.from_user.id == OPERATOR_ID:
                bot.send_message(OPERATOR_ID, f'Вы вышли из диалога! \n\nНажмите /start - для входа в меню')
                bot.send_message(client_id, f'Оператор завершил диалог с вами')
            else:
                bot.send_message(client_id, f'Вы вышли из диалога\n\nНажмите /start - для входа в меню')
                bot.send_message(OPERATOR_ID, f'Клиент завершил диалог с вами')
            REDIS.delete(f'client_id_for_dialogue')
        except Exception as e:
            logger.error(f'{e}')
            not_dialogs(call.from_user.id, bot)
    
    
    def not_dialogs(user_id: int, bot):
        if user_id == OPERATOR_ID:
            bot.delete_state(OPERATOR_ID, OPERATOR_ID)
            bot.send_message(OPERATOR_ID, 'Все диалоги закрыты')
        else:
            bot.delete_state(user_id, user_id)
            bot.send_message(user_id, f'Нажмите /start - для входа в меню')




#### Клавиатура 


    def keyboard_for_tests():
        poll_type = KeyboardButtonPollType(type='quiz')
        keyboard = types.ReplyKeyboardMarkup(input_field_placeholder='Выберите вопрос:', is_persistent=True)
        key1 = types.KeyboardButton(text='1', request_poll=poll_type)
        key2 = types.KeyboardButton(text='2')
        key3 = types.KeyboardButton(text='3')
        key4 = types.KeyboardButton(text='4')
        key5 = types.KeyboardButton(text='5')
        key6 = types.KeyboardButton(text='6')
        key7 = types.KeyboardButton(text='7')
        key8 = types.KeyboardButton(text='8')
        key9 = types.KeyboardButton(text='9')
        key10 = types.KeyboardButton(text='10')
        key11 = types.KeyboardButton(text='11')
        key12 = types.KeyboardButton(text='12')
        key13 = types.KeyboardButton(text='13')
        key14 = types.KeyboardButton(text='14')
        key15 = types.KeyboardButton(text='15')
        keyboard.add(key1, key2, key3, key4, key5, key6,
                     key7, key8, key9, key10, key11, key12, key13, key14, key15)
        return keyboard




### категории
    DIRECTIONS = set(i[1] for i in get_data_briefings())
    SUB_DIRECTIONS = set(i[2] for i in get_data_briefings() if type(i[2]) == str)
    SECTIONS = set(i[3] for i in get_data_briefings())



get_sections_from_db(callback.data.split('|')[0], callback.data.split('|')[1])[0][0]


### Клавиатура вопросов
    def keyboard_for_questions(path):
        logger.info(f'Клавиатуру вопросов: {path}')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        if len(path.split('|')) == 2:   # если мы перешли с dir|sec
            list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[1])
            for i in list_of_questions:
                keyboard.add(types.InlineKeyboardButton(text=i[0], callback_data=f'{path}|{i[0]}'), row_width=2)
                logger.info(f'В keyboard_for_questions Созданы callbackи: {path}|{i[0]}')
        if len(path.split('|')) == 3:   # если мы перешли с dir|sub|sec
            list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[2], path.split('|')[1])
            for i in list_of_questions:
                keyboard.add(types.InlineKeyboardButton(text=i[0], callback_data=f'{path}|{i[0]}'))
                logger.info(f'В keyboard_for_questions Созданы callbackи: {path}|{i[0]}')
        cancel = types.InlineKeyboardButton(text='Выйти', callback_data='cancel_from_test')
        keyboard.add(cancel)
        return keyboard

    import json
    json_string = "{'user_id': 34543543, 'add': '1'}"
    {'user_id': 34543543, 'add': '1'}
    dictionary = json.loads(json_string.replace("'", '"'))



#### На всякий клава для вопросов: 

    def keyboard_for_questions(path):
        logger.info(f'Клавиатуру вопросов: {path}')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        if len(path.split('|')) == 2:   # если мы перешли с dir|sec
            list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[1])
    
            for i in list_of_questions:
                keyboard.add(types.InlineKeyboardButton(text=i[1], callback_data=f'{path}|{i[0]}'))
                logger.info(f'В keyboard_for_questions Созданы callbackи: {path}|{i[0]}')
        if len(path.split('|')) == 3:   # если мы перешли с dir|sub|sec
            list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[2], path.split('|')[1])
            for i in list_of_questions:
                keyboard.add(types.InlineKeyboardButton(text=i[1], callback_data=f'{path}|{i[0]}'))
                logger.info(f'В keyboard_for_questions Созданы callbackи: {path}|{i[0]}')
        cancel = types.InlineKeyboardButton(text='Выйти', callback_data='cancel_from_inline_menu')
        keyboard.add(cancel)
        return keyboard



### Для тестов 




###  Загрузить файл в БД

    def add_document_to_db(user_id: int, tech_doc=None, cp_doc=None):
        if tech_doc is not None and cp_doc is None:
            execute(
                sql='''INSERT INTO documents_of_clients (tech_doc, client_id) VALUES (%s, %s)''',
                params=[(tech_doc, user_id)])
        elif cp_doc is not None and tech_doc is None:
            execute(
                sql='''INSERT INTO documents_of_clients (CP_doc, client_id) VALUES (%s, %s)''',
                params=[(cp_doc, user_id)])
        else:
            raise 'В аргументе должен быть всего 1 файл'
    
    
    def get_document_from_db(user_id: int, tech_doc=None, cp_doc=None):
        if tech_doc is not None and cp_doc is None:
            doc = fetch_one(
                sql='''SELECT tech_doc FROM documents_of_clients WHERE id = %s''',
                params=(user_id,))
        elif cp_doc is not None and tech_doc is None:
            doc = fetch_one(
                sql='''SELECT CP_doc FROM documents_of_clients WHERE id = %s''',
                params=(user_id,))
        else:
            raise 'В аргументе должен быть всего 1 файл'
        return doc
    
    if __name__ == '__main__':
        pass
        # with open('cp_document.docx', 'wb') as f:
        #     x = get_document_from_db(5432693304, tech_doc=True)
        #     f.write(x)
    
    
    CREATE TABLE documents_of_clients (
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        id BIGINT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        CP_doc BLOB,
        tech_doc BLOB,
        client_id BIGINT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    );



### Создание опросников 

    bot.send_message(message.chat.id, "Ответьте на вопрос")
    answer_options = ["кофе", "чай", "спать", "сок"]

    bot.send_poll(
        chat_id=message.chat.id,
        question="Чего бы вы хотели",
        options=answer_options,
        type="quiz",
        correct_option_id=3,
        explanation='Не тот вариант))',
        is_anonymous=False,
    )



### Выборка из базы данных 

    SELECT questions.id, questions.question_text, COALESCE(clients_briefings.user_response, 'Ответа нет') AS answer_text
    FROM questions
    LEFT JOIN clients_briefings ON questions.id = clients_briefings.question_id AND clients_briefings.client_id = 123
    WHERE questions.id = 2;