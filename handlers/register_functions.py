from handlers.commands import ClientCommands, OperatorCommands, GeneralCommands, PartnerCommands
from handlers import get_info
from handlers.callbacks import ClientCallbacks, OperatorCallbacks, GamesCallbacks, GeneralCallbacks
from handlers.get_info import UserRegistration, DialogWithOperator
from handlers.keyboards import GeneralKeyboards, ClientKeyboards, OperatorKeyboards
from services.filters import CheckPhoneNumber, ContactForm, CheckConsent, CheckFile, CheckClient, \
    CheckSubDirectory, CheckSection, SendAnswer, CheckOperator, CheckTextOnlyInMessage, \
    CheckDocumentInMessage, CheckPhotoInMessage, CheckChangeQuestion, CheckPartner, UserType, CheckAddQuestion, \
    CheckQuestionNumber
from services.states import GeneralStates, OperatorStates
from services.string_parser import Parser


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
               SendAnswer(),
               CheckTextOnlyInMessage(),
               CheckDocumentInMessage(),
               CheckPhotoInMessage(),
               CheckChangeQuestion(),
               CheckAddQuestion(),
               CheckQuestionNumber(),
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
    bot.register_message_handler(commands=['cancel'], state="*", callback=GeneralCommands.cancel_to_main_menu, pass_bot=True,
                                 client=True)
    # PARTNER
    bot.register_message_handler(commands=['start'], callback=PartnerCommands.start, pass_bot=True, partner=True)
    bot.register_message_handler(commands=['cancel'], state="*", callback=GeneralCommands.cancel_to_main_menu, pass_bot=True,
                                 partner=True)


def registration_file_handling(bot):
    """  Регистрация функций обработки файлов  """
    bot.register_message_handler(state=GeneralStates.get_technical_task_file,
                                 callback=get_info.get_technical_task_file, pass_bot=True, document=True)
    bot.register_message_handler(state=GeneralStates.get_commercial_offer_file,
                                 callback=get_info.get_commercial_offer_file, pass_bot=True, document=True)
    bot.register_message_handler(state=GeneralStates.get_other_file,
                                 callback=get_info.get_other_file, pass_bot=True, document=True)
    bot.register_message_handler(state=GeneralStates.get_report_file,
                                 callback=get_info.get_report_file, pass_bot=True, document=True)
    bot.register_message_handler(state=(GeneralStates.get_technical_task_file, GeneralStates.get_commercial_offer_file,
                                        GeneralStates.get_report_file, GeneralStates.get_other_file,
                                        OperatorStates.get_technical_task_file_in_dialogue,
                                        OperatorStates.get_commercial_offer_file_in_dialogue,
                                        OperatorStates.get_report_file_in_dialogue,
                                        OperatorStates.get_other_file_in_dialogue),
                                 callback=get_info.file_incorrect, pass_bot=True, document=False)

    # OPERATOR
    bot.register_message_handler(state=OperatorStates.get_technical_task_file_in_dialogue,
                                 callback=get_info.get_technical_task_file_from_dialogue, pass_bot=True, document=True)
    bot.register_message_handler(state=OperatorStates.get_commercial_offer_file_in_dialogue,
                                 callback=get_info.get_commercial_offer_file_from_dialogue, pass_bot=True,
                                 document=True)
    bot.register_message_handler(state=OperatorStates.get_report_file_in_dialogue,
                                 callback=get_info.get_report_file_from_dialogue, pass_bot=True, document=True)

    bot.register_message_handler(state=OperatorStates.get_other_file_in_dialogue,
                                 callback=get_info.get_other_file_from_dialogue, pass_bot=True, document=True)


def registration_states(bot):
    """   Регистрация состояний пользователя """
    bot.register_message_handler(text=['Отменить'], callback=GeneralCommands.cancel_to_start_registration,
                                 pass_bot=True, client=False, operator=False, partner=False)
    bot.register_message_handler(state="*", text=['Отменить'], callback=GeneralCommands.cancel_to_main_menu, pass_bot=True,
                                 client=True)
    bot.register_message_handler(state="*", text=['Отменить'], callback=GeneralCommands.cancel_to_main_menu, pass_bot=True,
                                 partner=True)
    bot.register_message_handler(state=GeneralStates.answer_to_question, text=['К вопросам'],
                                 callback=GeneralCommands.cancel_to_questions, pass_bot=True,
                                 client=True)
    bot.register_message_handler(state=GeneralStates.answer_to_question, text=['К вопросам'],
                                 callback=GeneralCommands.cancel_to_questions, pass_bot=True,
                                 partner=True)
    bot.register_message_handler(state=GeneralStates.answer_to_question, callback=get_info.next_question, pass_bot=True,
                                 text=['Следующий вопрос'], in_the_range_of_questions=True)
    bot.register_message_handler(state=GeneralStates.answer_to_question, callback=get_info.no_next_question,
                                 pass_bot=True,
                                 text=['Следующий вопрос'], in_the_range_of_questions=False)

    # USER REGISTRATION
    bot.register_message_handler(state=GeneralStates.name, callback=UserRegistration.get_user_name, pass_bot=True)
    bot.register_message_handler(state=GeneralStates.phone_number, callback=UserRegistration.get_user_phone,
                                 pass_bot=True,
                                 contact_form=True, check_phone=False)
    bot.register_message_handler(state=GeneralStates.phone_number, callback=UserRegistration.get_user_phone,
                                 pass_bot=True,
                                 check_phone=True)
    bot.register_message_handler(state=GeneralStates.phone_number, callback=UserRegistration.phone_incorrect,
                                 pass_bot=True,
                                 check_phone=False)
    bot.register_message_handler(state=GeneralStates.website, callback=UserRegistration.get_user_website, pass_bot=True)
    bot.register_message_handler(state=GeneralStates.company, callback=UserRegistration.get_user_company, pass_bot=True)


    # DIALOGUE WITH OPERATOR
    bot.register_message_handler(state=GeneralStates.request_for_dialogue,
                                 callback=DialogWithOperator.send_request_to_operator,
                                 pass_bot=True)
    bot.register_message_handler(state=GeneralStates.dialogue_with_operator,
                                 callback=DialogWithOperator.send_message_to_operator, pass_bot=True, text_only=True)
    bot.register_message_handler(state=GeneralStates.dialogue_with_operator,
                                 callback=DialogWithOperator.send_document_to_operator, pass_bot=True, document=True)
    bot.register_message_handler(state=GeneralStates.dialogue_with_operator,
                                 callback=DialogWithOperator.send_photo_to_operator, pass_bot=True, photo=True)

    bot.register_message_handler(state=GeneralStates.answer_to_question, callback=get_info.get_answer_from_user,
                                 pass_bot=True, send_answer=False)
    bot.register_message_handler(state=GeneralStates.answer_to_question, callback=get_info.send_user_answers_to_db,
                                 pass_bot=True, send_answer=True)

    # OPERATOR
    bot.register_message_handler(state=OperatorStates.change_question, callback=get_info.operator_change_question,
                                 pass_bot=True, operator=True, check_question=True)
    bot.register_message_handler(state=OperatorStates.change_question, callback=get_info.incorrect_change_question,
                                 pass_bot=True, operator=True, check_question=False)
    bot.register_message_handler(state=OperatorStates.dialogue_with_client,
                                 callback=DialogWithOperator.send_message_to_client, pass_bot=True, text_only=True)
    bot.register_message_handler(state=OperatorStates.dialogue_with_client,
                                 callback=DialogWithOperator.send_document_to_client, pass_bot=True, document=True)
    bot.register_message_handler(state=OperatorStates.dialogue_with_client,
                                 callback=DialogWithOperator.send_photo_to_client,
                                 pass_bot=True, photo=True)
    bot.register_message_handler(state=OperatorStates.add_question, callback=get_info.operator_add_question,
                                 pass_bot=True, operator=True, check_question=True)
    bot.register_message_handler(state=OperatorStates.add_question, callback=get_info.incorrect_change_question,
                                 pass_bot=True, operator=True, check_question=False)

    # ChatGPT (Блог)
    bot.register_message_handler(state=GeneralStates.chat_gpt, callback=get_info.get_question_from_user_for_chat_gpt,
                                 pass_bot=True)



def registration_games(bot):
    """  Регистрация игр  """
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_games,
                                        callback=GamesCallbacks.call_choose_game, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_karatekido2,
                                        callback=GamesCallbacks.call_send_game_1, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_qubo,
                                        callback=GamesCallbacks.call_send_game_2, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_basketboyrush,
                                        callback=GamesCallbacks.call_send_game_3, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_spikyfish3,
                                        callback=GamesCallbacks.call_send_game_4, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_basketboy,
                                        callback=GamesCallbacks.call_send_game_5, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == GeneralKeyboards.data_gravityninjaemeraldcity,
        callback=GamesCallbacks.call_send_game_6, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_keepitup,
                                        callback=GamesCallbacks.call_send_game_7, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GeneralKeyboards.data_karatekido2,
        callback=GamesCallbacks.call_game_1, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.game_short_name == GeneralKeyboards.data_qubo,
                                        callback=GamesCallbacks.call_game_2, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GeneralKeyboards.data_basketboyrush,
        callback=GamesCallbacks.call_game_3, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GeneralKeyboards.data_spikyfish3,
        callback=GamesCallbacks.call_game_4, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GeneralKeyboards.data_basketboy,
        callback=GamesCallbacks.call_game_5, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GeneralKeyboards.data_gravityninjaemeraldcity,
        callback=GamesCallbacks.call_game_6, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.game_short_name == GeneralKeyboards.data_keepitup,
        callback=GamesCallbacks.call_game_7, pass_bot=True)


def registration_menu_navigation(bot):
    """   Регистрация обработчиков нажатий на клавиатуру   """

    # GENERAL

    bot.register_callback_query_handler(func=lambda callback: callback.data in GeneralKeyboards.data_directory,
                                        callback=GeneralCallbacks.call_directory, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_briefing,
                                        callback=GeneralCallbacks.call_briefing, pass_bot=True, operator=False)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == GeneralKeyboards.data_cancel_to_directions,
        callback=GeneralCallbacks.call_cancel_to_directions, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=GeneralCallbacks.call_section, pass_bot=True, section=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=GeneralCallbacks.call_sub_directory, pass_bot=True, sub_directory=True)

    # PARTNER
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_enter_menu,
                                        callback=GeneralCallbacks.call_enter_menu, pass_bot=True, partner=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_question,
        callback=GeneralCallbacks.call_question, pass_bot=True, partner=True)

    # CLIENT
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_enter_menu,
                                        callback=GeneralCallbacks.call_enter_menu, pass_bot=True, client=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_back_to_questions,
                                        callback=ClientCallbacks.call_back_to_questions, pass_bot=True, client=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_files,
                                        callback=ClientCallbacks.call_file_types, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_chat,
                                        callback=ClientCallbacks.call_chat_with_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_instant_message,
                                        callback=ClientCallbacks.call_instant_messaging_service, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_blog,
                                        callback=ClientCallbacks.call_blog, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_question,
        callback=GeneralCallbacks.call_question, pass_bot=True, client=True)

    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == ClientKeyboards.data_gen_tech_exercise,
        callback=ClientCallbacks.call_generation_technical_exercise, pass_bot=True)

    # OPERATOR
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_change_question,
                                        callback=GeneralCallbacks.call_briefing, pass_bot=True, operator=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_add_question,
                                        callback=OperatorCallbacks.call_add_question, pass_bot=True, operator=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_back_to_questions,
                                        callback=OperatorCallbacks.call_back_to_questions, pass_bot=True, operator=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == GeneralKeyboards.data_enter_menu,
                                        callback=OperatorCallbacks.call_enter_menu, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_get_documents,
        callback=OperatorCallbacks.call_file_types, pass_bot=True, operator=True)

    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_client_info,
        callback=OperatorCallbacks.call_client_info, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_enter_dialog,
        callback=OperatorCallbacks.call_enter_into_a_dialog, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_dialog_history,
        callback=OperatorCallbacks.call_get_dialogue_history, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientKeyboards.data_change_answer,
                                        callback=ClientCallbacks.call_change_answer, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientKeyboards.data_technical_tasks,
                                        callback=ClientCallbacks.call_technical_tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientKeyboards.data_commercial_offers,
                                        callback=ClientCallbacks.call_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientKeyboards.data_reports,
                                        callback=ClientCallbacks.call_reports, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == ClientKeyboards.data_documents,
                                        callback=ClientCallbacks.call_documents, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorKeyboards.data_upload_file_in_dialogue,
        callback=OperatorCallbacks.call_upload_file_in_dialogue, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_question,
        callback=OperatorCallbacks.call_change_question, pass_bot=True, operator=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_upload_file,
                                        callback=OperatorCallbacks.call_upload_file, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_menu_in_dialogue,
                                        callback=OperatorCallbacks.call_enter_menu_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_queue,
        callback=OperatorCallbacks.call_queue, pass_bot=True)

    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_requests,
                                        callback=OperatorCallbacks.call_requests, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_clients,
                                        callback=OperatorCallbacks.call_clients, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_tasks,
                                        callback=OperatorCallbacks.call_tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_settings,
                                        callback=OperatorCallbacks.call_settings, pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_get_file,
        callback=OperatorCallbacks.call_get_file_in_dialogue, state=OperatorStates.dialogue_with_client,
        pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_get_file,
        callback=OperatorCallbacks.call_get_file, pass_bot=True, operator=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == GeneralKeyboards.data_get_file,
        callback=OperatorCallbacks.call_get_file, pass_bot=True, operator=False)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorKeyboards.data_tech_tasks_in_dialogue,
        callback=OperatorCallbacks.call_technical_tasks_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorKeyboards.data_com_offers_in_dialogue,
        callback=OperatorCallbacks.call_commercial_offers_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorKeyboards.data_reports_in_dialogue,
        callback=OperatorCallbacks.call_reports_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: callback.data == OperatorKeyboards.data_other_documents_in_dialogue,
        callback=OperatorCallbacks.call_other_documents_in_dialogue, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_show_tech_tasks,
        callback=OperatorCallbacks.call_client_technical_tasks, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_show_com_offers,
        callback=OperatorCallbacks.call_client_commercial_offers, pass_bot=True)
    bot.register_callback_query_handler(
        func=lambda callback: Parser.parse_callback(callback.data) == OperatorKeyboards.data_show_reports,
        callback=OperatorCallbacks.call_client_reports, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: Parser.parse_callback(
        callback.data) == OperatorKeyboards.data_show_other_documents,
                                        callback=OperatorCallbacks.call_client_other_documents, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == OperatorKeyboards.data_end_dialogue,
                                        callback=OperatorCallbacks.call_left_dialog, pass_bot=True, operator=True)

    bot.register_callback_query_handler(
        func=lambda callback: ClientKeyboards.data_evaluate or ClientKeyboards.data_do_not_evaluate == callback.data,
        callback=ClientCallbacks.call_grade, pass_bot=True)


def registration_all_functions_for_telegram_bot(bot):
    registration_filters(bot)
    registration_commands(bot)
    registration_file_handling(bot)
    registration_states(bot)
    registration_games(bot)
    registration_menu_navigation(bot)
