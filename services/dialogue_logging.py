import logging
import os

from config import DIR_FOR_SAVE_DIALOGS


def dialogue_logging(user_id: int):
    log_dialogue_in_file = logging.getLogger(f'logger_for_dialogue_{user_id}')
    if not log_dialogue_in_file.handlers:
        log_dir = f'{DIR_FOR_SAVE_DIALOGS}/{user_id}'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = logging.FileHandler(f'{DIR_FOR_SAVE_DIALOGS}/{user_id}/dialogue.log')
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        log_dialogue_in_file.addHandler(file_handler)
        log_dialogue_in_file.setLevel(logging.INFO)
        log_dialogue_in_file.propagate = False
    return log_dialogue_in_file
