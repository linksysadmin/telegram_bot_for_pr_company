from handlers.callback_handlers import general_callback, client_callback, operator_callback, game_callback
from handlers.command_handlers import unauthorized_command, operator_command, client_command, partner_command
from handlers.message_handlers import UserRegistration, DialogWithOperator, TextButtons, ChatGPT, \
    FileHandler, AnswerHandler, QuestionHandler
from handlers.keyboards import general_keyboard, client_keyboard, operator_keyboard

from services.filters import register_filters

from services.states import GeneralStates, OperatorStates

from config import bot
from services.string_parser import Parser
from services.tg_games import games


class RegisterTelegramFunctions:

    def __init__(self):
        self.user_reg = UserRegistration()
        self.dialog = DialogWithOperator()
        self.text_buttons = TextButtons()
        self.chat_gpt = ChatGPT()
        self.file = FileHandler()
        self.answer = AnswerHandler()
        self.question = QuestionHandler()

        self.register_commands()
        self.registration_file_handling()
        self.registration_states()
        self.register_games()
        self.register_callbacks()
        # self.registration_games()
        # self.registration_menu_navigation()
        register_filters()

    def register_commands(self):
        """   Регистрация команд telegram бота """

        COMMANDS = {
            'unauthorized': {'start': unauthorized_command.start},
            'operator': {'start': operator_command.start, 'test': operator_command.test},
            'client': {'start': client_command.start, 'test': client_command.test, 'cancel': client_command.cancel},
            'partner': {'start': partner_command.start, 'cancel': partner_command.cancel},
        }

        user_flags = {
            'unauthorized': {'client': False, 'partner': False, 'operator': False},
            'client': {'client': True},
            'operator': {'operator': True},
            'partner': {'partner': True}
        }

        for user, commands in COMMANDS.items():
            for command, function in commands.items():
                flags = user_flags[user]

                handler_args = {'commands': [command], 'callback': function, **flags}

                # Если текущая команда - 'cancel', добавляем state='*'
                if command == 'cancel':
                    handler_args['state'] = "*"

                bot.register_message_handler(**handler_args)

    def registration_file_handling(self):
        """  Регистрация функций обработки файлов  """
        bot.register_message_handler(state=GeneralStates.get_technical_task_file,
                                     callback=self.file.get_technical_task_file, document=True)
        bot.register_message_handler(state=GeneralStates.get_commercial_offer_file,
                                     callback=self.file.get_commercial_offer_file,
                                     document=True)
        bot.register_message_handler(state=GeneralStates.get_other_file,
                                     callback=self.file.get_other_file, document=True)
        bot.register_message_handler(state=GeneralStates.get_report_file,
                                     callback=self.file.get_report_file, document=True)
        bot.register_message_handler(
            state=(GeneralStates.get_technical_task_file, GeneralStates.get_commercial_offer_file,
                   GeneralStates.get_report_file, GeneralStates.get_other_file,
                   OperatorStates.get_technical_task_file_in_dialogue,
                   OperatorStates.get_commercial_offer_file_in_dialogue,
                   OperatorStates.get_report_file_in_dialogue,
                   OperatorStates.get_other_file_in_dialogue),
            callback=self.file.file_incorrect, document=False)

        # OPERATOR
        bot.register_message_handler(state=OperatorStates.get_technical_task_file_in_dialogue,
                                     callback=self.file.get_technical_task_file_from_dialogue,
                                     document=True)
        bot.register_message_handler(state=OperatorStates.get_commercial_offer_file_in_dialogue,
                                     callback=self.file.get_commercial_offer_file_from_dialogue,
                                     document=True)
        bot.register_message_handler(state=OperatorStates.get_report_file_in_dialogue,
                                     callback=self.file.get_report_file_from_dialogue,
                                     document=True)

        bot.register_message_handler(state=OperatorStates.get_other_file_in_dialogue,
                                     callback=self.file.get_other_file_from_dialogue,
                                     document=True)

    def registration_states(self):
        """   Регистрация состояний пользователя """

        bot.register_message_handler(text=['Отменить'], callback=self.text_buttons.cancel_to_start_registration,
                                     client=False, operator=False, partner=False)

        bot.register_message_handler(state="*", text=['Отменить'],
                                     callback=client_command.cancel,
                                     client=True)
        bot.register_message_handler(state="*", text=['Отменить'],
                                     callback=partner_command.cancel,
                                     partner=True)

        bot.register_message_handler(state=GeneralStates.answer_to_question, text=['К вопросам'],
                                     callback=self.text_buttons.cancel_to_questions,
                                     client=True)
        bot.register_message_handler(state=GeneralStates.answer_to_question, text=['К вопросам'],
                                     callback=self.text_buttons.cancel_to_questions,
                                     partner=True)
        bot.register_message_handler(state=GeneralStates.answer_to_question,
                                     callback=self.text_buttons.next_question,
                                     text=['Следующий вопрос'], in_the_range_of_questions=True)
        bot.register_message_handler(state=GeneralStates.answer_to_question,
                                     callback=self.text_buttons.no_next_question,
                                     text=['Следующий вопрос'], in_the_range_of_questions=False)

        # USER REGISTRATION
        bot.register_message_handler(state=GeneralStates.name, callback=self.user_reg.get_user_name)
        bot.register_message_handler(state=GeneralStates.phone_number, callback=self.user_reg.get_user_phone,
                                     contact_form=True, check_phone=False)
        bot.register_message_handler(state=GeneralStates.phone_number, callback=self.user_reg.get_user_phone,
                                     check_phone=True)
        bot.register_message_handler(state=GeneralStates.phone_number, callback=self.user_reg.phone_incorrect,
                                     check_phone=False)
        bot.register_message_handler(state=GeneralStates.website, callback=self.user_reg.get_user_website, )
        bot.register_message_handler(state=GeneralStates.company, callback=self.user_reg.get_user_company, )

        # DIALOGUE WITH OPERATOR
        bot.register_message_handler(state=GeneralStates.request_for_dialogue,
                                     callback=self.dialog.send_request_to_operator, )
        bot.register_message_handler(state=GeneralStates.dialogue_with_operator,
                                     callback=self.dialog.send_message_to_operator,
                                     text_only=True)
        bot.register_message_handler(state=GeneralStates.dialogue_with_operator,
                                     callback=self.dialog.send_document_to_operator,
                                     document=True)
        bot.register_message_handler(state=GeneralStates.dialogue_with_operator,
                                     callback=self.dialog.send_photo_to_operator,
                                     photo=True)
        bot.register_message_handler(state=GeneralStates.answer_to_question,
                                     callback=self.answer.get_answer_from_user, send_answer=False)
        bot.register_message_handler(state=GeneralStates.answer_to_question,
                                     callback=self.answer.send_user_answers_to_db, send_answer=True)
        bot.register_message_handler(state=OperatorStates.dialogue_with_client,
                                     callback=self.dialog.send_message_to_client, text_only=True)
        bot.register_message_handler(state=OperatorStates.dialogue_with_client,
                                     callback=self.dialog.send_document_to_client, document=True)
        bot.register_message_handler(state=OperatorStates.dialogue_with_client,
                                     callback=self.dialog.send_photo_to_client, photo=True)

        # OPERATOR
        bot.register_message_handler(state=OperatorStates.change_question,
                                     callback=self.question.operator_change_question, operator=True,
                                     check_question=True)
        bot.register_message_handler(state=OperatorStates.change_question,
                                     callback=self.question.incorrect_change_question, operator=True,
                                     check_question=False)
        bot.register_message_handler(state=OperatorStates.add_question,
                                     callback=self.question.operator_add_question, operator=True,
                                     check_question=True)
        bot.register_message_handler(state=OperatorStates.add_question,
                                     callback=self.question.incorrect_change_question, operator=True,
                                     check_question=False)

        # ChatGPT (Блог)
        bot.register_message_handler(state=GeneralStates.chat_gpt,
                                     callback=self.chat_gpt.get_question_from_user_for_chat_gpt)

    def register_games(self):
        """  Регистрация игр  """

        bot.register_callback_query_handler(func=lambda callback: callback.data == general_keyboard.game_button.data,
                                            callback=game_callback.choose_game)
        #
        bot.register_callback_query_handler(func=lambda callback: callback.data in games.get_list_short_names(),
                                            callback=game_callback.send_game)
        #
        bot.register_callback_query_handler(
            func=lambda callback: callback.game_short_name in games.get_list_short_names(),
            callback=game_callback.game)

    def register_callbacks(self):
        """   Регистрация обработчиков нажатий на клавиатуру   """

        # GENERAL

        bot.register_callback_query_handler(
            func=lambda callback: callback.data in general_keyboard.directory_button.data(),
            callback=general_callback.directory)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == general_keyboard.briefing_button.data,
            callback=general_callback.briefing, operator=False)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == general_keyboard.cancel_to_directions_button.data,
            callback=general_callback.cancel_to_directions)
        bot.register_callback_query_handler(func=lambda callback: callback.data,
                                            callback=general_callback.section, section=True)
        bot.register_callback_query_handler(func=lambda callback: callback.data,
                                            callback=general_callback.sub_directory,
                                            sub_directory=True)

        # PARTNER
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == general_keyboard.enter_menu_for_client_button.data,
            callback=general_callback.enter_menu, partner=True)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == general_keyboard.question_button.data,
            callback=general_callback.question, partner=True)

        # CLIENT
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == general_keyboard.enter_menu_for_client_button.data,
            callback=general_callback.enter_menu, client=True)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == client_keyboard.back_to_questions_client_button.data,
            callback=client_callback.back_to_questions, client=True)

        bot.register_callback_query_handler(func=lambda callback: callback.data == general_keyboard.files_button.data,
                                            callback=client_callback.file_types)
        bot.register_callback_query_handler(func=lambda callback: callback.data == general_keyboard.chat_button.data,
                                            callback=client_callback.chat_with_operator)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == general_keyboard.instant_message_button.data,
            callback=client_callback.instant_messaging_service)
        bot.register_callback_query_handler(func=lambda callback: callback.data == client_keyboard.blog_button.data,
                                            callback=client_callback.blog)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == general_keyboard.question_button.data,
            callback=general_callback.question, client=True)

        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == client_keyboard.tex_button.data,
            callback=client_callback.generation_technical_exercise)

        # OPERATOR
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.change_question_button.data,
            callback=general_callback.briefing, operator=True)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.add_question_button.data,
            callback=operator_callback.add_question, operator=True)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.back_to_questions_button.data,
            callback=operator_callback.back_to_questions, operator=True)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == general_keyboard.enter_menu_for_client_button.data,
            callback=operator_callback.enter_menu,
            operator=True)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == operator_keyboard.get_documents_button.data,
            callback=operator_callback.file_types, operator=True)

        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == operator_keyboard.client_info_button.data,
            callback=operator_callback.client_info)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(
                callback.data) == operator_keyboard.enter_into_a_dialog_button.data,
            callback=operator_callback.enter_into_a_dialog, operator=True)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(
                callback.data) == operator_keyboard.dialogue_history_button.data,
            callback=operator_callback.get_dialogue_history)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == client_keyboard.change_answer_button.data,
            callback=client_callback.change_answer)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == client_keyboard.technical_tasks_button.data,
            callback=client_callback.technical_task)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == client_keyboard.commercial_offers_button.data,
            callback=client_callback.commercial_offer)
        bot.register_callback_query_handler(func=lambda callback: callback.data == client_keyboard.reports_button.data,
                                            callback=client_callback.reports)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == client_keyboard.documents_button.data,
            callback=client_callback.documents)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.upload_file_in_dialogue_button.data,
            callback=operator_callback.upload_file_in_dialogue)

        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == general_keyboard.question_button.data,
            callback=operator_callback.change_question, operator=True)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.upload_file_button.data,
            callback=operator_callback.upload_file)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.operator_menu_in_dialogue_button.data,
            callback=operator_callback.enter_menu_in_dialogue)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == operator_keyboard.queue_button.data,
            callback=operator_callback.queue)

        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.requests_button.data,
            callback=operator_callback.requests)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.clients_button.data,
            callback=operator_callback.clients)
        bot.register_callback_query_handler(func=lambda callback: callback.data == operator_keyboard.tasks_button.data,
                                            callback=operator_callback.tasks)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.settings_button.data,
            callback=operator_callback.settings)

        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(
                callback.data) == operator_keyboard.get_file_in_dialogue_operator_button.data,
            callback=operator_callback.get_file_in_dialogue, state=OperatorStates.dialogue_with_client,
            operator=True)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(
                callback.data) == operator_keyboard.get_file_for_operator_button.data,
            callback=operator_callback.get_file, operator=True)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == client_keyboard.get_file_button.data,
            callback=client_callback.get_file, operator=False)
        bot.register_callback_query_handler(
            func=lambda
                callback: callback.data == operator_keyboard.technical_tasks_for_operator_in_dialogue_button.data,
            callback=operator_callback.technical_tasks_in_dialogue)
        bot.register_callback_query_handler(
            func=lambda
                callback: callback.data == operator_keyboard.commercial_offers_for_operator_in_dialogue_button.data,
            callback=operator_callback.commercial_offers_in_dialogue)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.reports_for_operator_in_dialogue_button.data,
            callback=operator_callback.reports_in_dialogue)
        bot.register_callback_query_handler(
            func=lambda
                callback: callback.data == operator_keyboard.other_documents_for_operator_in_dialogue_button.data,
            callback=operator_callback.other_documents_in_dialogue)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == operator_keyboard.tt_operator_button.data,
            callback=operator_callback.client_technical_tasks)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == operator_keyboard.co_operator_button.data,
            callback=operator_callback.client_commercial_offers)
        bot.register_callback_query_handler(
            func=lambda callback: Parser.parse_callback(callback.data) == operator_keyboard.r_operator_button.data,
            callback=operator_callback.client_reports)
        bot.register_callback_query_handler(func=lambda callback: Parser.parse_callback(
            callback.data) == operator_keyboard.od_operator_button.data,
                                            callback=operator_callback.client_other_documents)
        bot.register_callback_query_handler(
            func=lambda callback: callback.data == operator_keyboard.end_the_dialogue_button.data,
            callback=operator_callback.left_dialog, operator=True)

        bot.register_callback_query_handler(
            func=lambda
                callback: client_keyboard.client_grade_yes_button.data or client_keyboard.client_grade_no_button.data == callback.data,
            callback=client_callback.grade)
