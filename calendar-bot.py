import model
import telebot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class BotExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        print(f'Error in bot: {exception}')
        return True


bot = telebot.TeleBot(model.select_token(), exception_handler=BotExceptionHandler())

bot.set_my_commands([
    telebot.types.BotCommand('/start', 'Начало работы'),
    telebot.types.BotCommand('/meeting', 'Работа со встречами'),
    telebot.types.BotCommand('/admin', 'Управление')
])

COMMANDS_MEETING = {
    1: {
        'name': 'Добавить встречу',
        'function': None
    },
    2: {
        'name': 'Удалить встречу',
        'function': None
    },
    3: {
        'name': 'Показать встречи',
        'function': None
    }
}


@bot.message_handler(commands=['start'])
def start(message):
    model.upsert_chat(message.chat.id, message.chat.username, message.chat.title)
    bot.send_message(message.chat.id, 'Все отлично! Можно работать 👌')


@bot.message_handler(commands=['meeting'])
def meeting(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 6
    for key, value in COMMANDS_MEETING.items():
        markup.add(InlineKeyboardButton(text=value['name'], callback_data=f'command_{key}'))
    add_cancel_button(markup)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


# region bot utils
def add_cancel_button(markup):
    markup.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
# endregion
