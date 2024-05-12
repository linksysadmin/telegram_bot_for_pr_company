

class User:

    def __init__(self):
        self.__name = ''

    @property
    def name(self):
        return self.__name


class Operator(User):

    def __init__(self):
        super().__init__()
        self.__name = 'operator'


class Client(User):

    def __init__(self):
        super().__init__()
        self.__name = 'client'


class Partner(User):

    def __init__(self):
        super().__init__()
        self.__name = 'partner'


class UnauthorizedUser(User):

    def __init__(self):
        super().__init__()
        self.__name = 'unauthorized_user'


unauthorized_user = UnauthorizedUser()
operator = Operator()
client = Client()
partner = Partner()

