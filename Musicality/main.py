import requests, config, parser, aiogram

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage  
from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(StatesGroup):
    Song_Name = State()
    Artist_Name = State()


bot = Bot(token = config.TOKEN)

memoryStorage = MemoryStorage()

dp = Dispatcher(bot = bot, storage = memoryStorage)


async def clear_chat_and_new_game(chat_id):
    user = config.DICT_USER_INSTANCE[chat_id]

    for n in range(user.MESSAGE_ID_LIST[0], user.MESSAGE_ID_LIST[-1] + 1):
        if n not in user.MESSAGE_ID_LIST:
            user.MESSAGE_ID_LIST.append(n)

    for id in sorted(user.MESSAGE_ID_LIST, reverse = True):
        await bot.delete_message(chat_id = chat_id, message_id = id)

    last_message_id = sorted(user.MESSAGE_ID_LIST)[-1]

    user.MESSAGE_ID_LIST.clear()

    await bot.send_message(chat_id = chat_id, text = 'Ваша статистика', reply_markup = SwitchKeyboardMarkup('/start'))

    user.MESSAGE_ID_LIST.append(last_message_id + 1)

    await bot.send_message(
        chat_id = chat_id, 
        text = config.MESSAGE_TEXT % (
            user.username, 
            user.true_answer,
            user.wrong_answer
        )
    )

    user.MESSAGE_ID_LIST.append(last_message_id + 2)


def SwitchKeyboardMarkup(attr):
    ReplyKeyboard = ReplyKeyboardMarkup(resize_keyboard = True)

    if attr == '/start' or attr == 'Ответить':
        ReplyKeyboard.add(KeyboardButton('Сгенерировать песню'))
    elif attr == 'Сгенерировать песню':
        ReplyKeyboard.add(KeyboardButton('Ответить'), KeyboardButton('Незнаю'))
    elif attr == 'Незнаю':
        ReplyKeyboard.add(KeyboardButton('Продолжить'))

    return ReplyKeyboard


async def edit_statistic_message(chat_id):
    user = config.DICT_USER_INSTANCE[chat_id]

    try:
        await bot.edit_message_text(
            chat_id = chat_id, 
            message_id = user.STATISTIC_MESSAGE_ID, 
            text = config.MESSAGE_TEXT % (
                user.username, 
                user.true_answer, 
                user.wrong_answer
            )
        )

    except aiogram.utils.exceptions.MessageToEditNotFound:
        pass


@dp.message_handler(state = UserState.Song_Name)
async def input_Song_Name(message: types.Message, state: FSMContext):
    await state.update_data(song_name = message.text.lower())

    await message.answer(text = "Укажите исполнителя")

    await state.set_state(UserState.Artist_Name.state)

    await UserState.Artist_Name.set()


@dp.message_handler(state = UserState.Artist_Name)
async def input_Artist_Name(message: types.Message, state: FSMContext):
    user = config.DICT_USER_INSTANCE[message.chat.id]

    await state.update_data(artist_name = message.text.lower())

    data = await state.get_data()

    if f'{data["artist_name"]} - {data["song_name"]}' == user.SONG_INFO.lower():
        await message.answer(text = 'Вы ответили верно', reply_markup = SwitchKeyboardMarkup(attr = 'Незнаю'))
        user.MESSAGE_ID_LIST.append(message.message_id + 1)
        user.true_answer += 1
    else:
        await message.answer(text = 'Вы ответили неправильно', reply_markup = SwitchKeyboardMarkup(attr = 'Незнаю'))
        await message.answer(text = f'Правильный ответ: {user.SONG_INFO}')
        user.MESSAGE_ID_LIST.append(message.message_id + 2)
        user.wrong_answer += 1

    await edit_statistic_message(chat_id = message.chat.id)

    await state.finish()


@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    user = config.User()

    config.DICT_USER_INSTANCE[message.chat.id] = user

    user.MESSAGE_ID_LIST.append(message.message_id)

    user.username = f'{message.chat.first_name}  {message.chat.last_name}'.replace('None', '')

    user.STATISTIC_MESSAGE_ID = message.message_id + 2

    await message.answer(text = 'Ваша статистика', reply_markup = SwitchKeyboardMarkup(attr = message.text))

    await message.answer(
        text = config.MESSAGE_TEXT % (
            user.username, 
            user.true_answer,
            user.wrong_answer
        )
    )


@dp.message_handler(content_types = ['text'])
async def startGame(message: types.Message):
    user = config.DICT_USER_INSTANCE[message.chat.id]

    user.MESSAGE_ID_LIST.append(message.message_id)

    if message.text == 'Сгенерировать песню':

        # Отправляем сообщение и удаляем клавиатуру
        await message.answer(text = 'Подождите... Подбираю песню', reply_markup = types.ReplyKeyboardRemove())

        INFO, URL = parser.getURL()

        user.SONG_INFO = INFO

        response = bytearray(requests.get(url = URL).content)

        if b'TIT2' in response:
            track = response[:response.find(b'TIT2') + 4] + response[response.find(b'TPE1'):]

        else:
            track = response[:response.find(b'TSSE')] + b'TIT2' + response[response.find(b'TSSE'):]

        await message.answer_audio(
            audio = track, 
            title = 'Угадай песню',
            performer = 'Угадай исполнителя',
            thumb = open(config.IMAGE_PATH, 'rb'), 
            reply_markup = SwitchKeyboardMarkup(attr = message.text)
        )


    elif message.text == 'Ответить':
        # Отправляем сообщение и удаляем клавиатуру
        await message.answer('Укажите название песни', reply_markup = types.ReplyKeyboardRemove())

        await UserState.Song_Name.set()


    elif message.text == 'Незнаю':
        user.wrong_answer += 1

        await edit_statistic_message(chat_id = message.chat.id)

        await message.answer(text = f'Правильный ответ: {user.SONG_INFO}', reply_markup = SwitchKeyboardMarkup(attr = message.text))

        user.MESSAGE_ID_LIST.append(message.message_id + 1)

    elif message.text == 'Продолжить':
        await clear_chat_and_new_game(message.chat.id)


if __name__ == '__main__':
    executor.start_polling(dispatcher = dp)
