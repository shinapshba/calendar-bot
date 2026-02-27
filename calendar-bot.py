import functions
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

functions_admin = functions.Admin(bot)

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

COMMANDS_ADMIN = {
    4: {
        'name': 'Показать пользователей',
        'function': functions_admin.show_users
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


@bot.message_handler(commands=['admin'])
def admin(message):
    if model.is_super_user(message.from_user.username):
        markup = InlineKeyboardMarkup()
        markup.row_width = 6
        for key, value in COMMANDS_ADMIN.items():
            markup.add(InlineKeyboardButton(text=value['name'], callback_data=f'command_{key}'))
        add_cancel_button(markup)
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Управление доступно только администраторам бота 🔒')


@bot.callback_query_handler(func=lambda call: call.data.startswith('command_'))
def command_callback_handler(call):
    command_id = int(call.data.replace('command_', ''))
    if command_id in COMMANDS_MEETING:
        COMMANDS_MEETING[command_id]['function'](call)  # noqa
    if command_id in COMMANDS_ADMIN:
        COMMANDS_ADMIN[command_id]['function'](call)  # noqa
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel'))
def cancel_callback_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)


def add_cancel_button(markup):
    markup.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))


updates = bot.get_updates()
if updates:
    last_update_id = updates[-1].update_id
    bot.get_updates(offset=last_update_id + 1)

bot.polling(none_stop=True, interval=0, skip_pending=True)
