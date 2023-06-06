from handlers.keyboards import keyboard_for_games


def callback_choose_game(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите игру:',
                          reply_markup=keyboard_for_games())


def callback_send_game_1(call, bot):
    bot.send_game(call.from_user.id, game_short_name='karatekido2')


def callback_send_game_2(call, bot):
    bot.send_game(call.from_user.id, game_short_name='qubo')


def callback_send_game_3(call, bot):
    bot.send_game(call.from_user.id, game_short_name='basketboyrush')


def callback_send_game_4(call, bot):
    bot.send_game(call.from_user.id, game_short_name='spikyfish3')


def callback_send_game_5(call, bot):
    bot.send_game(call.from_user.id, game_short_name='basketboy')


def callback_send_game_6(call, bot):
    bot.send_game(call.from_user.id, game_short_name='gravityninjaemeraldcity')


def callback_send_game_7(call, bot):
    bot.send_game(call.from_user.id, game_short_name='keepitup')


def callback_game_1(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/karatekid2-48c08d62bc7684c7c0020cac16b8c81d12073454#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3DxzfhXSL7MbG-2sflYJ0Z5TxBj5nfpLoTtmy207lo2r-XWUanrtG-u4B20VJrFu_l')


def callback_game_2(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/u0yXP5o-f4def4e95fbc17585cdcc1465e38469528a195bd#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3DWfol-cpOTGxh6ioc0qZLcOXYgJvg3qa9OmrHSHKeT-ldiZK-A0TGKimgNwL_-hpB')


def callback_game_3(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/qxpwxJTh7-cd8fea3257629021cc34acaa33799c7386288a00#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3Dj4_TubsjkwN2p7cIVzBOZwPB7TBxsv_VXxc8EyU_C5h6kMon2QyRPeQJQ960-tua')


def callback_game_4(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/zcvFFeQ0t-5cce2e3225abc237098cd630f4e1a73d65a1afce#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3DMAsVu3j2g_mKfmj1R939qSI1eHhTxktZhwu0miJJp3O06N0rNQ1uWozOpta-jcvB')


def callback_game_5(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/DwVcZZnbP-abd015ce95140f9779ee25dfcb67839c1a5163ec#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3DStfTVwLidbvNiOU7VQYjE2BOVEZeRy_90flL2sERv8rTu3x_2fMA0XQzDemGeDie')


def callback_game_6(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/gravityninjaemeraldcity-d52b84dc3d0cc986aee23b1ea66c49be28da32e5#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3DED5pUS3GGDpVbeFjDahLO2vYTLms6VSDcMnN5_LdKZP4CbX0gYpOu7XEW5pQM4y9')


def callback_game_7(call, bot):
    bot.answer_callback_query(call.id,
                              url='https://prizes.gamee.com/game-bot/a3pyHGoadz-c70a910a834b64c83d52e3ef7383882a690c43c8#tgShareScoreUrl=tg%3A%2F%2Fshare_game_score%3Fhash%3DghQFcTbzufK9mFJk3vEDu9CV10QyjI1zFpk8H1EkhyAwO7WNf_7qZiJW1KytJxdH')
