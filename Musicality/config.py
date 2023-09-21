class User:

    def __init__(self):
        self.username = str()
        self.true_answer = 0
        self.wrong_answer = 0
        
        self.SONG_INFO = dict()
        

DICT_USER_INSTANCE = dict()

QUANTITY_VARIANTS_ANSWER = 4

TOKEN = '6620707317:AAEI5N0oBpZ9FxYiF82Sq7clAZiKBQ-24rM'

URL = 'https://muzofond.fm/'

IMAGE_PATH = './cover.jpg'

MESSAGE_TEXT = 'Пользователь: %s\n'\
    'Кол-во верных ответов: %s\n'\
    'Кол-во неправильных ответов: %s'
    