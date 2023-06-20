import logging

from services.db_data import get_directories

logger = logging.getLogger(__name__)


class BaseCallbacks:
    get_file = 'get|file|'
    get_documents = 'get_documents|'

    @staticmethod
    def parse_callback(data: str):
        try:
            list_of_callback_parts = data.split('|')
            list_of_callback_parts_without_last_element = list_of_callback_parts[:-1]
            callback = '|'.join(list_of_callback_parts_without_last_element) + '|'
            return callback
        except Exception as e:
            logger.error(e)
            return data


class ClientCallbacks(BaseCallbacks):
    briefing = "scenario"
    files = 'files'
    chat = 'chat'
    instant_message = 'instant_message'
    blog = 'blog'
    games = 'games'
    directory = get_directories()
    cancel_to_directions = 'cancel_to_directions'
    back_to_questions = 'back_to_questions'
    enter_menu = 'enter_menu'
    change_answer = 'change_answer'
    technical_tasks = 'technical_tasks'
    commercial_offers = 'commercial_offers'
    reports = 'reports'
    documents = 'documents'
    evaluate = 'client_grade_yes'
    do_not_evaluate = 'client_grade_no'
    question = 'question|'
    gen_tech_exercise = 'tex|'


class GamesCallbacks:
    karatekido2 = 'karatekido2'
    qubo = 'qubo'
    basketboyrush = 'basketboyrush'
    spikyfish3 = 'spikyfish3'
    basketboy = 'basketboy'
    gravityninjaemeraldcity = 'gravityninjaemeraldcity'
    keepitup = 'keepitup'


class OperatorCallbacks(BaseCallbacks):
    enter_dialog = "enter_into_a_dialog|"
    menu = 'operator_menu'
    menu_in_dialogue = 'operator_menu_in_dialogue'
    queue = 'queue|'
    requests = 'requests'
    clients = 'clients'
    tasks = 'tasks'
    settings = 'settings'
    change_question = 'change_question'
    add_question = 'add_question'
    client_info = "client|info|"
    tech_tasks_in_dialogue = 'technical_tasks_for_operator_in_dialogue'
    com_offers_in_dialogue = 'commercial_offers_for_operator_in_dialogue'
    reports_in_dialogue = 'reports_for_operator_in_dialogue'
    other_documents_in_dialogue = 'other_documents_for_operator_in_dialogue'
    upload_file = 'upload_file'
    upload_file_in_dialogue = 'upload_file_in_dialogue'
    show_tech_tasks = 'TT_for_operator|'
    show_com_offers = 'CO_operator|'
    show_reports = 'R_operator|'
    show_other_documents = 'OD_operator|'
    dialog_history = 'dialogue_history|'
    end_dialogue = 'end_the_dialogue'

