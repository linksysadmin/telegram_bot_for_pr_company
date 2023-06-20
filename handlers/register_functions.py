from handlers import dialog, clients, documents, operator, games
from handlers.clients import *
from handlers.commands import ClientCommands, OperatorCommands, delete_state_
from handlers.dialog import callback_enter_into_a_dialog, callback_client_info
from handlers import get_info
from handlers.operator import callback_get_dialogue_history, callback_menu_directions_of_documents
from services.callbacks import ClientCallbacks, OperatorCallbacks, GamesCallbacks, BaseCallbacks
from services.filters import CheckPhoneNumber, ContactForm, CheckConsent, CheckFile, CheckClient, \
    CheckSubDirectory, CheckSection, FinishPoll, NextQuestion, CheckOperator, CheckTextOnlyInMessage,\
    CheckDocumentInMessage, CheckPhotoInMessage
from services.states import MyStates


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
               CheckOperator(),
               CheckSubDirectory(),
               CheckSection(),
               FinishPoll(),
               NextQuestion(),
               CheckTextOnlyInMessage(),
               CheckDocumentInMessage(),
               CheckPhotoInMessage(),
               )

    for filter_ in FILTERS:
        bot.add_custom_filter(filter_)


def registration_commands(bot):
    """   Регистрация команд telegram бота """
    bot.register_message_handler(commands=['start'], callback=OperatorCommands.start, pass_bot=True, operator=True)
    bot.register_message_handler(commands=['start'], callback=ClientCommands.start, pass_bot=True, client=True)
    bot.register_message_handler(commands=['start'], callback=ClientCommands.start_unauthorized, pass_bot=True, client=False)
    bot.register_message_handler(commands=['test'], callback=OperatorCommands.test_, pass_bot=True, operator=True)
    bot.register_message_handler(commands=['cancel'], state="*", callback=delete_state_, pass_bot=True)


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
    bot.register_message_handler(state="*", text=['Отменить'], callback=delete_state_, pass_bot=True)
    bot.register_message_handler(state="*", text=['К вопросам'], callback=delete_state_, pass_bot=True)
    bot.register_message_handler(state=MyStates.request, callback=dialog.send_request_to_operator,
                                 pass_bot=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=dialog.send_message_to_operator, pass_bot=True, text_only=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=dialog.send_document_to_operator, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=dialog.send_photo_to_operator, pass_bot=True, photo=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=dialog.send_message_to_client, pass_bot=True, text_only=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=dialog.send_document_to_client, pass_bot=True, document=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=dialog.send_photo_to_client, pass_bot=True, photo=True)
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
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.briefing,
                                        callback=callback_scenario, pass_bot=True, client=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.files,
                                        callback=callback_technical_tasks_and_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.chat,
                                        callback=callback_chat_with_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.instant_message,
                                        callback=dialog.callback_instant_messaging_service, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.blog,
                                        callback=callback_blog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data in ClientCallbacks.directory,
                                        callback=callback_directory, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_section, pass_bot=True,
                                        section=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_sub_directory, pass_bot=True,
                                        sub_directory=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.back_to_questions,
                                        callback=callback_back_to_questions, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.enter_menu,
                                        callback=callback_cancel_from_inline_menu, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.cancel_to_directions,
                                        callback=callback_cancel_to_directions, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: OperatorCallbacks.parse_callback(callback.data) == OperatorCallbacks.client_info,
        callback=callback_client_info, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: OperatorCallbacks.parse_callback(callback.data) == OperatorCallbacks.enter_dialog,
        callback=callback_enter_into_a_dialog, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: OperatorCallbacks.parse_callback(callback.data) == OperatorCallbacks.dialog_history,
        callback=callback_get_dialogue_history, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_documents,
        callback=callback_menu_directions_of_documents, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_documents,
        callback=dialog.callback_operator_left_dialog, pass_bot=True,
        operator=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.change_answer,
                                        callback=callback_for_change_answer, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.technical_tasks,
                                        callback=callback_technical_tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.commercial_offers,
                                        callback=callback_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.reports,
                                        callback=callback_reports, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientCallbacks.documents,
                                        callback=callback_documents, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.upload_file_in_dialogue,
        callback=operator.callback_upload_file_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == ClientCallbacks.question,
        callback=callback_for_questions, pass_bot=True,
        client=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == ClientCallbacks.question,
        callback=callback_for_registration, pass_bot=True,
        client=False)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == ClientCallbacks.gen_tech_exercise,
        callback=documents.callback_for_registration_technical_exercise,
        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.menu,
                                        callback=operator.callback_cancel_to_enter_menu_for_operator,
                                        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.upload_file,
                                        callback=operator.callback_upload_file, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.menu_in_dialogue,
                                        callback=operator.callback_cancel_to_enter_menu_in_dialogue,
                                        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.queue,
        callback=operator.callback_queue, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.requests,
                                        callback=operator.callback_requests_for_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.clients,
                                        callback=operator.callback_clients_for_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.tasks,
                                        callback=operator.callback_tasks_for_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.settings,
                                        callback=operator.callback_settings_for_operator, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_file,
        callback=documents.callback_get_file_for_operator_in_dialogue,
        state=MyStates.dialogue_with_client, pass_bot=True,
        operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_file,
        callback=documents.callback_get_file_for_operator, pass_bot=True,
        operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == BaseCallbacks.get_file,
        callback=documents.callback_get_file_for_client, pass_bot=True,
        operator=False)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.tech_tasks_in_dialogue,
        callback=operator.callback_technical_tasks_for_operator_in_dialogue,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.com_offers_in_dialogue,
        callback=operator.callback_commercial_offers_for_operator_in_dialogue,
        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.reports_in_dialogue,
                                        callback=operator.callback_reports_for_operator_in_dialogue,
                                        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.other_documents_in_dialogue,
        callback=operator.callback_other_documents_for_operator_in_dialogue,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_tech_tasks,
        callback=operator.callback_client_technical_tasks_for_operator,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_com_offers,
        callback=operator.callback_client_commercial_offers_for_operator,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_reports,
        callback=operator.callback_client_reports_for_operator,
        pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: BaseCallbacks.parse_callback(callback.data) == OperatorCallbacks.show_other_documents,
        callback=operator.callback_client_other_documents_for_operator,
        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorCallbacks.end_dialogue,
                                        callback=dialog.callback_operator_left_dialog, pass_bot=True,
                                        operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: ClientCallbacks.evaluate or ClientCallbacks.do_not_evaluate == callback.data,
        callback=clients.callback_for_grade, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorCallbacks.change_question,
        callback=clients.callback_scenario, pass_bot=True, operator=True)


def registration_all_functions_for_telegram_bot(bot):
    registration_filters(bot)
    registration_commands(bot)
    registration_file_handling(bot)
    registration_states(bot)
    registration_games(bot)
    registration_menu_navigation(bot)
