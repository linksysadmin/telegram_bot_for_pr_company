from typing import List


class Game:
    def __init__(self, visual_name: str, official_name: str, url: str):
        self.__visual_name = visual_name
        self.__official_name = official_name
        self.__url = 'https://prizes.gamee.com/game-bot/' + url

    @property
    def visual_name(self):
        return self.__visual_name

    @property
    def official_name(self):
        return self.__official_name

    @property
    def url(self):
        return self.__url

    def __str__(self):
        return self.__official_name


class GameList:
    def __init__(self):
        self.__GAME_OBJECTS = []

    @property
    def list(self) -> List:
        return self.__GAME_OBJECTS

    def add(self, *args: 'Game'):
        for game in args:
            self.__GAME_OBJECTS.append(game)

    def get_list_short_names(self):
        return [game.official_name for game in self.__GAME_OBJECTS]

    def __len__(self):
        return len(self.__GAME_OBJECTS)


karatekido2 = Game('Karate Kido 2', 'karatekido2', 'karatekid2-48c08d62bc7684c7c0020cac16b8c81d12073454')
qubo = Game('Qubo', 'qubo', 'u0yXP5o-f4def4e95fbc17585cdcc1465e38469528a195bd')
basketboyrush = Game('Basket Boy Rush', 'basketboyrush', 'qxpwxJTh7-cd8fea3257629021cc34acaa33799c7386288a00')
spikyfish3 = Game('Spiky Fish 3', 'spikyfish3', 'zcvFFeQ0t-5cce2e3225abc237098cd630f4e1a73d65a1afce')
basketboy = Game('Basket Boy', 'basketboy', 'DwVcZZnbP-abd015ce95140f9779ee25dfcb67839c1a5163ec')
gravityninjaemeraldcity = Game('Gravity Ninja: Emerald City', 'gravityninjaemeraldcity',
                               'gravityninjaemeraldcity-d52b84dc3d0cc986aee23b1ea66c49be28da32e5')
keepitup = Game('Keep it UP', 'keepitup', 'a3pyHGoadz-c70a910a834b64c83d52e3ef7383882a690c43c8')

games = GameList()
games.add(karatekido2, qubo, basketboyrush, spikyfish3, basketboy, gravityninjaemeraldcity, keepitup)
