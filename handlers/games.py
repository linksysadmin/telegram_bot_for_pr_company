import logging

from handlers.keyboards import ClientKeyboards
from telebot import apihelper

from services.callbacks import GamesCallbacks

logger = logging.getLogger(__name__)


def callback_choose_game(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите игру:',
                          reply_markup=ClientKeyboards.games())


def callback_send_game_1(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.karatekido2)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_send_game_2(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.qubo)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_send_game_3(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.basketboyrush)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_send_game_4(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.spikyfish3)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_send_game_5(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.basketboy)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_send_game_6(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.gravityninjaemeraldcity)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_send_game_7(call, bot):
    try:
        bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.keepitup)
    except apihelper.ApiTelegramException:
        logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')


def callback_game_1(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/karatekid2-48c08d62bc7684c7c0020cac16b8c81d12073454')


def callback_game_2(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/u0yXP5o-f4def4e95fbc17585cdcc1465e38469528a195bd')


def callback_game_3(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/qxpwxJTh7-cd8fea3257629021cc34acaa33799c7386288a00')


def callback_game_4(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/zcvFFeQ0t-5cce2e3225abc237098cd630f4e1a73d65a1afce')


def callback_game_5(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/DwVcZZnbP-abd015ce95140f9779ee25dfcb67839c1a5163ec')


def callback_game_6(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/gravityninjaemeraldcity-d52b84dc3d0cc986aee23b1ea66c49be28da32e5')


def callback_game_7(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/a3pyHGoadz-c70a910a834b64c83d52e3ef7383882a690c43c8')
