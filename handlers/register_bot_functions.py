from handlers import dialog_with_operator, callbacks_for_clients, send_document_to_user, callbacks_for_operator, games
from handlers.callbacks_for_clients import callback_scenario, callback_technical_tasks_and_commercial_offer, \
    callback_chat_with_operator, callback_upload_report, callback_blog, callback_query_for_scenario, \
    callback_for_section, callback_for_sub_direction, callback_back_to_questions, callback_section_from_subcategory, \
    callback_cancel_from_inline_menu, callback_cancel_to_directions, callback_for_change_answer, \
    callback_technical_tasks, callback_commercial_offer, callback_for_questions, callback_for_registration
from handlers.commands import start_for_operator, start, start_unauthorized, delete_state_, test_
from handlers.get_info_from_user import get_user_name, phone_incorrect, get_user_phone, get_user_company, \
    get_answer_from_user, get_user_website, send_user_answers_to_db, next_question
from services.db_data import get_directories
from services.filters import CheckPhoneNumber, ContactForm, CheckConsent, CheckFile, CheckUserRegistration, \
    CheckPathToSection, CheckPathToSectionWithSubDirectory, CheckPathToSectionWithoutSubDirectory, FinishPoll, \
    NextQuestion, CheckOperator
from services.states import MyStates


def register_functions_for_bot(bot, custom_filters):
    """Регистрация команд, фильтров, состояний и функций обратного вызова для Телеграм-бота"""

    FILTERS = (custom_filters.StateFilter(bot),
               custom_filters.IsDigitFilter(),
               custom_filters.TextMatchFilter(),
               CheckPhoneNumber(),
               ContactForm(),
               CheckConsent(),
               CheckFile(),
               CheckUserRegistration(),
               CheckPathToSection(),
               CheckPathToSectionWithSubDirectory(),
               CheckPathToSectionWithoutSubDirectory(),
               FinishPoll(),
               NextQuestion(),
               CheckOperator(),
               )

    """   Регистрация команд telegram бота """
    bot.register_message_handler(commands=['start'], callback=start_for_operator, pass_bot=True, check_operator=True)
    bot.register_message_handler(commands=['start'], callback=start, pass_bot=True, check_user_registration=True)
    bot.register_message_handler(commands=['start'], callback=start_unauthorized, pass_bot=True,
                                 check_user_registration=False)
    bot.register_message_handler(state="*", callback=delete_state_, commands=['cancel'], pass_bot=True)
    bot.register_message_handler(commands=['test'], callback=test_, pass_bot=True)

    """   Добавление фильтров сообщений   """
    for filter_ in FILTERS:
        bot.add_custom_filter(filter_)

    """   Регистрация состояний пользователя   """
    bot.register_message_handler(state="*", text=['Отменить'], callback=delete_state_, pass_bot=True)
    bot.register_message_handler(state="*", text=['К вопросам'], callback=delete_state_, pass_bot=True)
    bot.register_message_handler(state=MyStates.request, callback=dialog_with_operator.send_request_to_operator,
                                 pass_bot=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=dialog_with_operator.send_message_to_operator, pass_bot=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=dialog_with_operator.send_message_to_client, pass_bot=True)
    bot.register_message_handler(state=MyStates.name, callback=get_user_name, pass_bot=True)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_user_phone, pass_bot=True, contact_form=True,
                                 check_phone=False)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_user_phone, pass_bot=True, check_phone=True)
    bot.register_message_handler(state=MyStates.phone_number, callback=phone_incorrect, pass_bot=True,
                                 check_phone=False)
    bot.register_message_handler(state=MyStates.website, callback=get_user_website, pass_bot=True)
    bot.register_message_handler(state=MyStates.company, callback=get_user_company, pass_bot=True)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=next_question, pass_bot=True,
                                 next_question=True)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=get_answer_from_user, pass_bot=True,
                                 finish_poll=False)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=send_user_answers_to_db, pass_bot=True,
                                 finish_poll=True)

    """  Регистрация игр  """
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'karatekido2',
                                        callback=games.callback_send_game_1, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'qubo',
                                        callback=games.callback_send_game_2, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'basketboyrush',
                                        callback=games.callback_send_game_3, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'spikyfish3',
                                        callback=games.callback_send_game_4, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'basketboy',
                                        callback=games.callback_send_game_5, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'gravityninjaemeraldcity',
                                        callback=games.callback_send_game_6, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'keepitup',
                                        callback=games.callback_send_game_7, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'karatekido2',
                                        callback=games.callback_game_1, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'qubo',
                                        callback=games.callback_game_2, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'basketboyrush',
                                        callback=games.callback_game_3, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'spikyfish3',
                                        callback=games.callback_game_4, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'basketboy',
                                        callback=games.callback_game_5, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'gravityninjaemeraldcity',
                                        callback=games.callback_game_6, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == 'keepitup',
                                        callback=games.callback_game_7, pass_bot=True)

    """   Регистрация обработчиков нажатий на клавиатуру   """

    bot.register_callback_query_handler(func=lambda callback: callback.data == "scenario",
                                        callback=callback_scenario, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "technical_tasks_and_commercial_offer",
                                        callback=callback_technical_tasks_and_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "chat_with_operator",
                                        callback=callback_chat_with_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "instant_messaging_service",
                                        callback=dialog_with_operator.callback_instant_messaging_service, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "upload_report",
                                        callback=callback_upload_report, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "blog",
                                        callback=callback_blog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data in get_directories(),
                                        callback=callback_query_for_scenario, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_for_section, pass_bot=True,
                                        path_to_section_without_sub_directory=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_for_sub_direction, pass_bot=True,
                                        path_to_section=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_section_from_subcategory, pass_bot=True,
                                        path_to_section_with_sub_directory=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'back_to_questions',
                                        callback=callback_back_to_questions, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == "cancel_from_inline_menu",
                                        callback=callback_cancel_from_inline_menu, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "cancel_to_directions",
                                        callback=callback_cancel_to_directions, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "enter_into_a_dialog",
                                        callback=dialog_with_operator.callback_enter_into_a_dialog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "cancel_from_dialog",
                                        callback=dialog_with_operator.callback_cancel_from_dialog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "change_answer",
                                        callback=callback_for_change_answer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "technical_tasks",
                                        callback=callback_technical_tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "commercial_offers",
                                        callback=callback_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'games',
                                        callback=games.callback_choose_game, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: "question_" in callback.data,
                                        callback=callback_for_questions, pass_bot=True,
                                        check_user_registration=True)
    bot.register_callback_query_handler(func=lambda callback: "question_" in callback.data,
                                        callback=callback_for_registration, pass_bot=True,
                                        check_user_registration=False)
    bot.register_callback_query_handler(func=lambda callback: 'tex_' in callback.data,
                                        callback=send_document_to_user.callback_for_registration_technical_exercise,
                                        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'cancel_to_enter_menu_for_operator',
                                        callback=callbacks_for_operator.callback_cancel_to_enter_menu_for_operator,
                                        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: 'queue_' in callback.data,
                                        callback=callbacks_for_operator.callback_queue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data in ('requests', 'clients', 'tasks', 'settings'),
        callback=callbacks_for_operator.callback_for_enter_menu, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: 'send_file_' in callback.data,
                                        callback=send_document_to_user.callback_for_send_file, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'technical_tasks_for_operator',
                                        callback=callbacks_for_operator.callback_technical_tasks_for_operator,
                                        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: 'client_grade_yes' or 'client_grade_yes' == callback.data,
                                        callback=callbacks_for_clients.callback_for_grade, pass_bot=True)
