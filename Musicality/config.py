class User:

    def __init__(self):
        self.username = str()
        self.true_answer = 0
        self.wrong_answer = 0
        
        self.SONG_INFO = str()
        self.STATISTIC_MESSAGE_ID = 0
        self.MESSAGE_ID_LIST = list()


DICT_USER_INSTANCE = dict()

TOKEN = '6391335447:AAEqhWoMJAbodUrnTwnZicuFOr42yVv_oBo'

URL = 'https://muzofond.fm/'

IMAGE_PATH = '.\\cover.jpg'

MESSAGE_TEXT = 'Пользователь: %s\n'\
    'Кол-во верных ответов: %s\n'\
    'Кол-во неправильных ответов: %s'
    