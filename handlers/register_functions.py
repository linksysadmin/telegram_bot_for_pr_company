from handlers import documents, games
from handlers.commands import ClientCommands, OperatorCommands, GeneralCommands
from handlers import get_info
from handlers.callback_handlers import OperatorCallbackHandlers, ClientCallbackHandlers, BaseCallbackHandlers
from services.callbacks import ClientCallbacks, OperatorCallbacks, GamesCallbacks, BaseCallbacks
from services.filters import CheckPhoneNumber, ContactForm, CheckConsent, CheckFile, CheckClient, \
    CheckSubDirectory, CheckSection, FinishPoll, NextQuestion, CheckOperator, CheckTextOnlyInMessage, \
    CheckDocumentInMessage, CheckPhotoInMessage, CheckChangeQuestion, CheckPartner, UserType
from services.states import MyStates, OperatorStates


def registration_filters(bot):
    """   Добавление фильтров сообщений   """
    from telebot import custom_filters
    FILTERS = (custom_filters.StateFilter(bot),
               custom_filters.IsDigitFilter(),
               custom_filters.TextMatchFilter(),
               CheckPhoneNumber(),
               ContactForm(),
               CheckConsent(),
               CheckFile(),
               CheckClient(),
               CheckPartner(),
               UserType(),
               CheckOperator(),
               CheckSubDirectory(),
               CheckSection(),
               FinishPoll(),
               NextQuestion(),
               CheckTextOnlyInMessage(),
               CheckDocumentInMessage(),
               CheckPhotoInMessage(),
               CheckChangeQuestion(),
               )

    for filter_ in FILTERS:
        bot.add_custom_filter(filter_)


def registration_commands(bot):
    """   Регистрация команд telegram бота """
    # GENERAL
    bot.register_message_handler(commands=['start'], callback=GeneralCommands.start_unauthorized, pass_bot=True,
                                 client=False, partner=False, operator=False)

    # OPERATOR
    bot.register_message_handler(commands=['start'], callback=OperatorCommands.start, pass_bot=True, operator=True)
    bot.register_message_handler(commands=['test'], callback=OperatorCommands.test_, pass_bot=True, operator=True)

    # CLIENT
    bot.register_message_handler(commands=['start'], callback=ClientCommands.start, pass_bot=True, client=True)
    bot.register_message_handler(commands=['cancel'], state="*", callback=ClientCommands.cancel, pass_bot=True,
                                 client=True)


def registration_file_handling(bot):
    """  Регистрация функций обработки файлов  """
    bot.register_message_handler(state=MyStates.get_technical_task_file,
                                 callback=get_info.get_technical_task_file, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.get_commercial_offer_file,
                                 callback=get_info.get_commercial_offer_file, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.get_report_file_in_dialogue,
                                 callback=get_info.get_report_file, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.get_other_file,
                                 callback=get_info.get_other_file, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.get_technical_task_file_in_dialogue,
                                 callback=get_info.get_technical_task_file_from_dialogue, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.get_commercial_offer_file_in_dialogue,
                                 callback=get_info.get_commercial_offer_file_from_dialogue, pass_bot=True,
                                 document=True)
    bot.register_message_handler(state=MyStates.get_report_file_in_dialogue,
                                 callback=get_info.get_report_file_from_dialogue, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.get_other_file_in_dialogue,
                                 callback=get_info.get_other_file_from_dialogue, pass_bot=True, document=True)
    bot.register_message_handler(state=[MyStates.get_technical_task_file, MyStates.get_commercial_offer_file,
                                        MyStates.get_report_file, MyStates.get_other_file,
                                        MyStates.get_technical_task_file_in_dialogue,
                                        MyStates.get_commercial_offer_file_in_dialogue,
                                        MyStates.get_report_file_in_dialogue, MyStates.get_other_file_in_dialogue],
                                 callback=get_info.file_incorrect, pass_bot=True, document=False)


def registration_states(bot):
    """   Регистрация состояний пользователя   """
    bot.register_message_handler(state="*", text=['Отменить'], callback=GeneralCommands.cancel, pass_bot=True, client=False, operator=False, partner=False)
    bot.register_message_handler(state="*", text=['Отменить'], callback=ClientCommands.cancel, pass_bot=True, client=True)
    bot.register_message_handler(state="*", text=['К вопросам'], callback=ClientCommands.cancel, pass_bot=True, client=True)
    bot.register_message_handler(state=MyStates.request, callback=get_info.send_request_to_operator,
                                 pass_bot=True)

    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=get_info.send_message_to_operator, pass_bot=True, text_only=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=get_info.send_document_to_operator, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=get_info.send_photo_to_operator, pass_bot=True, photo=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=get_info.send_message_to_client, pass_bot=True, text_only=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=get_info.send_document_to_client, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=get_info.send_photo_to_client, pass_bot=True, photo=True)

    bot.register_message_handler(state=MyStates.type_of_user, callback=get_info.get_type_of_user, pass_bot=True, user_type=True)
    bot.register_message_handler(state=MyStates.type_of_user, callback=get_info.user_type_incorrect, pass_bot=True, user_type=False)
    bot.register_message_handler(state=MyStates.name, callback=get_info.get_user_name, pass_bot=True)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_info.get_user_phone, pass_bot=True,
                                 contact_form=True,
                                 check_phone=False)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_info.get_user_phone, pass_bot=True,
                                 check_phone=True)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_info.phone_incorrect, pass_bot=True,
                                 check_phone=False)
    bot.register_message_handler(state=MyStates.website, callback=get_info.get_user_website, pass_bot=True)
    bot.register_message_handler(state=MyStates.company, callback=get_info.get_user_company, pass_bot=True)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=get_info.next_question, pass_bot=True,
                                 next_question=True)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=get_info.get_answer_from_user,
                                 pass_bot=True,
                                 finish_poll=False)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=get_info.send_user_answers_to_db,
                                 pass_bot=True,
                                 finish_poll=True)
    bot.register_message_handler(state=OperatorStates.change_question, callback=get_info.operator_change_question,
                                 pass_bot=True, operator=True, check_question=True)
    bot.register_message_handler(state=OperatorStates.change_question, callback=get_info.incorrect_change_question,
                                 pass_bot=True, operator=True, check_question=False)
    # bot.register_message_handler(state=OperatorStates.add_question, callback=get_info.operator_change_question,
    #                              pass_bot=True, operator=True, check_question=True)
    # bot.register_message_handler(state=OperatorStates.add_question, callback=get_info.incorrect_change_question,
    #                              pass_bot=True, operator=True, check_question=False)


def registration_games(bot):
    """  Регистрация игр  """
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.games,
                                        callback=games.callback_choose_game, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.karatekido2,
                                        callback=games.callback_send_game_1, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.qubo,
                                        callback=games.callback_send_game_2, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.basketboyrush,
                                        callback=games.callback_send_game_3, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.spikyfish3,
                                        callback=games.callback_send_game_4, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.basketboy,
                                        callback=games.callback_send_game_5, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.gravityninjaemeraldcity,
                                        callback=games.callback_send_game_6, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GamesCallbacks.keepitup,
                                        callback=games.callback_send_game_7, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GamesCallbacks.karatekido2,
                                        callback=games.callback_game_1, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GamesCallbacks.qubo,
                                        callback=games.callback_game_2, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GamesCallbacks.basketboyrush,
                                        callback=games.callback_game_3, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GamesCallbacks.spikyfish3,
                                        callback=games.callback_game_4, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GamesCallbacks.basketboy,
                                        callback=games.callback_game_5, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GamesCallbacks.gravityninjaemeraldcity,
        callback=games.callback_game_6, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GamesCallbacks.keepitup,
                                        callback=games.callback_game_7, pass_bot=True)


def registration_menu_navigation(bot):
    """   Регистрация обработчиков нажатий на клавиатуру   """

    # GENERAL
    bot.register_callback_query_handler(func=lambda callback: callback.data == BaseCallbacks.back_to_questions,
                                        callback=BaseCallbackHandlers.back_to_questions, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data in BaseCallbacks.directory,
                                        callback=BaseCallbackHandlers.directory, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == BaseCallbacks.briefing,
                                        callback=BaseCallbackHandlers.briefing, pass_bot=True, client=True)

    # CLIENT
    bot.register_callback_query_handler(func=lambda callback: callback.data == BaseCallbacks.enter_menu,
                                        callback=ClientCallbackHandlers.enter_menu, pass_bot=True, client=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.files,
                                        callback=ClientCallbackHandlers.file_types, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.chat,
                                        callback=ClientCallbackHandlers.chat_with_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.instant_message,
                                        callback=ClientCallbackHandlers.instant_messaging_service, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.blog,
                                        callback=ClientCallbackHandlers.blog, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=BaseCallbackHandlers.section, pass_bot=True,
                                        section=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=BaseCallbackHandlers.sub_directory, pass_bot=True,
                                        sub_directory=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == BaseCallbacks.cancel_to_directions,
                                        callback=BaseCallbackHandlers.cancel_to_directions, pass_bot=True)

    # OPERATOR
    bot.register_callback_query_handler(func=lambda callback: callback.data == BaseCallbacks.enter_menu,
                                        callback=OperatorCallbackHandlers.enter_menu, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_documents,
        callback=OperatorCallbackHandlers.file_types, pass_bot=True, operator=True)

    bot.register_callback_query_handler(
        func=lambda callback: OperatorCallbacks.parse_callback(callback.data) == OperatorCallbacks.client_info,
        callback=OperatorCallbackHandlers.client_info, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: OperatorCallbacks.parse_callback(callback.data) == OperatorCallbacks.enter_dialog,
        callback=OperatorCallbackHandlers.enter_into_a_dialog, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: OperatorCallbacks.parse_callback(callback.data) == OperatorCallbacks.dialog_history,
        callback=OperatorCallbackHandlers.get_dialogue_history, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.change_answer,
                                        callback=ClientCallbackHandlers.change_answer, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.technical_tasks,
                                        callback=ClientCallbackHandlers.technical_tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.commercial_offers,
                                        callback=ClientCallbackHandlers.commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.reports,
                                        callback=ClientCallbackHandlers.reports, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.documents,
                                        callback=ClientCallbackHandlers.documents, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.upload_file_in_dialogue,
        callback=OperatorCallbackHandlers.upload_file_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.question,
        callback=ClientCallbackHandlers.questions, pass_bot=True, client=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.question,
        callback=OperatorCallbackHandlers.change_question, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == ClientCallbacks.gen_tech_exercise,
        callback=documents.callback_for_registration_technical_exercise, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.upload_file,
                                        callback=OperatorCallbackHandlers.upload_file, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.menu_in_dialogue,
                                        callback=OperatorCallbackHandlers.enter_menu_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.queue,
        callback=OperatorCallbackHandlers.queue, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.requests,
                                        callback=OperatorCallbackHandlers.requests, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.clients,
                                        callback=OperatorCallbackHandlers.clients, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.tasks,
                                        callback=OperatorCallbackHandlers.tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.settings,
                                        callback=OperatorCallbackHandlers.settings, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_file,
        callback=documents.callback_get_file_for_operator_in_dialogue,
        state=MyStates.dialogue_with_client, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_file,
        callback=documents.callback_get_file_for_operator, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_file,
        callback=documents.callback_get_file_for_client, pass_bot=True, operator=False)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.tech_tasks_in_dialogue,
        callback=OperatorCallbackHandlers.technical_tasks_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.com_offers_in_dialogue,
        callback=OperatorCallbackHandlers.commercial_offers_in_dialogue,
        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.reports_in_dialogue,
                                        callback=OperatorCallbackHandlers.reports_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.other_documents_in_dialogue,
        callback=OperatorCallbackHandlers.other_documents_in_dialogue,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_tech_tasks,
        callback=OperatorCallbackHandlers.client_technical_tasks,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_com_offers,
        callback=OperatorCallbackHandlers.client_commercial_offers,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_reports,
        callback=OperatorCallbackHandlers.client_reports,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_other_documents,
        callback=OperatorCallbackHandlers.client_other_documents,
        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.end_dialogue,
                                        callback=OperatorCallbackHandlers.left_dialog, pass_bot=True,
                                        operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.change_question,
        callback=BaseCallbackHandlers.briefing, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.add_question,
        callback=OperatorCallbackHandlers.briefing, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: ClientCallbacks.evaluate or ClientCallbacks.do_not_evaluate == callback.data,
        callback=ClientCallbackHandlers.grade, pass_bot=True)


def registration_all_functions_for_telegram_bot(bot):
    registration_filters(bot)
    registration_commands(bot)
    registration_file_handling(bot)
    registration_states(bot)
    registration_games(bot)
    registration_menu_navigation(bot)
