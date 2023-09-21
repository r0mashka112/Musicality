import requests, config, parsing, random

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = Bot(token = config.TOKEN)

dp = Dispatcher(bot = bot)


async def SwitchKeyboardMarkup(attr) -> ReplyKeyboardMarkup:
    ReplyKeyboard = ReplyKeyboardMarkup(resize_keyboard = True)

    if attr == 'generate':
        ReplyKeyboard.add(KeyboardButton('Сгенерировать песню')).add(KeyboardButton('Моя статистика'))
    elif attr == 'answer':
        ReplyKeyboard.add(KeyboardButton('Ответить')).add(KeyboardButton('Не знаю'))

    return ReplyKeyboard


@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    user = config.User()

    if user not in config.DICT_USER_INSTANCE:
        config.DICT_USER_INSTANCE[message.chat.id] = user

    user.username = f'{message.chat.first_name}  {message.chat.last_name}'.replace('None', '')

    await message.answer('Hello', reply_markup = await SwitchKeyboardMarkup(attr = 'generate'))


async def make_keyboard(call, tag) -> InlineKeyboardMarkup:
    if type(call) is types.callback_query.CallbackQuery:
        user_object = config.DICT_USER_INSTANCE[call.message.chat.id]
    else:
        user_object = config.DICT_USER_INSTANCE[call.chat.id]

    list_audio_name = await parsing.get_list_button_items(class_tag = tag, object = user_object)
    
    r = random.randint(0, config.QUANTITY_VARIANTS_ANSWER - 1)

    print(r)

    if type(call) is types.callback_query.CallbackQuery:

        list_audio_name.insert(
            r, 
            config.DICT_USER_INSTANCE[call.message.chat.id].SONG_INFO[tag]
        )
    else:
        list_audio_name.insert(
            r, 
            config.DICT_USER_INSTANCE[call.chat.id].SONG_INFO[tag]    
        )

    keyboard = InlineKeyboardMarkup()

    for num, item in enumerate(list_audio_name):
        keyboard.add(InlineKeyboardButton(item, callback_data = f'btn-{tag}-{num}'))

    return keyboard


@dp.message_handler(content_types = ['text'])
async def startGame(message: types.Message):
    user = config.DICT_USER_INSTANCE[message.chat.id]

    if message.text == 'Сгенерировать песню':
        await message.answer(text = 'Подождите... Подбираю песню', reply_markup = types.ReplyKeyboardRemove())

        user.SONG_INFO, URL = await parsing.getAudio()

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
            reply_markup = await SwitchKeyboardMarkup(attr = 'answer')
        )

    elif message.text == 'Ответить':
        keyboard_track = await make_keyboard(call = message, tag = 'track')

        await message.answer('Попробуйте угадать название песни', reply_markup=types.ReplyKeyboardRemove())

        await message.answer(
            text = 'Выберите название песни', 
            reply_markup = keyboard_track
        )

    elif message.text == 'Не знаю':
        user.wrong_answer += 1

        await message.answer(
            text = f'Правильный ответ: {user.SONG_INFO["artist"]} - {user.SONG_INFO["track"]}', 
            reply_markup = await SwitchKeyboardMarkup(attr = 'generate')
        )

    elif message.text == 'Моя статистика':
        await message.answer(
            text = config.MESSAGE_TEXT % (
                user.username, 
                user.true_answer,
                user.wrong_answer
            ), 
            reply_markup = await SwitchKeyboardMarkup(attr = 'generate')
        )


async def check_answer(call, tag) -> bool:
    if config.DICT_USER_INSTANCE[call.message.chat.id].SONG_INFO[tag] == \
    call.message.reply_markup.inline_keyboard[int(call.data[-1])][0].text:
        return True
    else:
        return False
    

async def delete_msg_with_keyboard(call) -> None:
    await bot.delete_message(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
    )    
        

async def send_wrong_message(call) -> None:
    await call.message.answer(text = 'К сожалению, вы ошиблись')

    user_object = config.DICT_USER_INSTANCE[call.message.chat.id]

    await call.message.answer(
            text = f'Правильный ответ: {user_object.SONG_INFO["artist"]} - {user_object.SONG_INFO["track"]}', 
            reply_markup = await SwitchKeyboardMarkup(attr = 'generate')
        )
    
    config.DICT_USER_INSTANCE[call.message.chat.id].wrong_answer += 1


@dp.callback_query_handler(lambda call: call.data.startswith('btn-track'))
async def pushed_button_track(callback_query: types.CallbackQuery):
    await delete_msg_with_keyboard(call = callback_query)

    if await check_answer(callback_query, tag = 'track'):
        keyboard_artist = await make_keyboard(call = callback_query, tag = 'artist')

        await callback_query.message.answer('А теперь исполнителя', reply_markup=types.ReplyKeyboardRemove())

        await callback_query.message.answer(
            text = 'Выберите исполнителя', 
            reply_markup = keyboard_artist
        )
    else:
        await send_wrong_message(call = callback_query)


@dp.callback_query_handler(lambda call: call.data.startswith('btn-artist'))
async def pushed_button_artist(callback_query: types.CallbackQuery):
    await delete_msg_with_keyboard(call = callback_query)

    if await check_answer(callback_query, tag = 'artist'):

        await callback_query.message.answer(
            text = 'Вы ответили правильно!'
        )

        user_object = config.DICT_USER_INSTANCE[callback_query.message.chat.id]

        await callback_query.message.answer(
            text = f'Это {user_object.SONG_INFO["artist"]} - {user_object.SONG_INFO["track"]}', 
            reply_markup = await SwitchKeyboardMarkup('generate')
        )

        config.DICT_USER_INSTANCE[callback_query.message.chat.id].true_answer += 1
    else:
        await send_wrong_message(call = callback_query)


if __name__ == '__main__':
    executor.start_polling(dispatcher = dp)
