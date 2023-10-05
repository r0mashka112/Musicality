class User:

    def __init__(self):
        self.username = str()
        self.true_answer = 0
        self.wrong_answer = 0
        
        self.SONG_INFO = dict()
        

DICT_USER_INSTANCE = dict()

QUANTITY_VARIANTS_ANSWER = 4

TOKEN = '6636166160:AAHrned4WmRcx6bBdQ_fzBMW7oe6HXfoViw'

URL = 'https://muzofond.fm/'

IMAGE_PATH = './cover.jpg'

MESSAGE_TEXT = 'Пользователь: %s\n'\
    'Кол-во верных ответов: %s\n'\
    'Кол-во неправильных ответов: %s'
    