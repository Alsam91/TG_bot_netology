import random
import configparser
import os
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from create_db import TGBotDB

print('Start telegram bot...')

known_users = TGBotDB().user_list()
userStep = {}
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово'
    DELETE_WORD = 'Удалить слово'
    NEXT = 'Следующее'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


def bot_init():
    config = configparser.ConfigParser()
    config_file_path = os.getenv('CONFIG_FILE_PATH', 'config.ini')
    with open(config_file_path) as config_file:
        config.read_file(config_file)
    token_bot = config['tg']['token']
    state_storage = StateMemoryStorage()
    return TeleBot(token_bot, state_storage=state_storage)


bot = bot_init()


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        TGBotDB().add_user(cid)
        userStep[cid] = 0
        bot.send_message(cid, 'Здравствуйте, давайте изучать английский')
    else:
        userStep[cid] = 0
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    others = []
    get_word = random.sample(
        (TGBotDB().get_words() + TGBotDB().get_user_words(cid)), k=4)
    word = get_word[0]
    target_word = word[0]
    translate = word[1]
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    for word in get_word[1:]:
        others.append(word[0])
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выберите перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        cid = message.chat.id
        userStep[cid] = 2
        bot.send_message(cid,
                         "Введите слово, которое хотите удалить:")
        bot.set_state(
            message.from_user.id,
            MyStates.target_word,
            message.chat.id
        )


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.send_message(cid,
                     "Введи слово на английском и через пробел его перевод:")
    bot.set_state(
        message.from_user.id,
        MyStates.translate_word,
        message.chat.id
    )


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    bot_db = TGBotDB()
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    cid = message.chat.id
    all_words = []
    for i in (bot_db.get_words() + bot_db.get_user_words(cid)):
        all_words.append(i[0])
    if userStep[cid] == 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['target_word']
            if text == target_word:
                hint = show_target(data)
                hint_text = ["Отлично!❤", hint]
                next_btn = types.KeyboardButton(Command.NEXT)
                add_word_btn = types.KeyboardButton(Command.ADD_WORD)
                delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
                buttons.extend([next_btn, add_word_btn, delete_word_btn])
                hint = show_hint(*hint_text)
            else:
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                hint = show_hint(
                    "Допущена ошибка!",
                    f"Попробуй ещё раз вспомнить "
                    f"слово 🇷🇺{data['translate_word']}")
        markup.add(*buttons)
        bot.send_message(message.chat.id, hint, reply_markup=markup)
    elif userStep[cid] == 1:
        if text.split()[0] in all_words:
            bot.send_message(cid, "Такое слово уже есть в словаре")
        else:
            bot_db.add_user_word(cid, text)
            bot.send_message(cid, "Слово добавлено в словарь ✅")
            userStep[cid] = 0
            markup = types.ReplyKeyboardRemove()
        create_cards(message)
    elif userStep[cid] == 2:
        for wrds in bot_db.get_user_words(cid):
            if text not in wrds:
                bot.send_message(cid, "Такого слова нет в Вашем словаре")
            else:
                bot_db.delete_user_word(cid, text)
                bot.send_message(cid, "Слово удалено из Вашего словаря ✅")
                userStep[cid] = 0
                markup = types.ReplyKeyboardRemove()
            create_cards(message)
    else:
        create_cards(message)


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
