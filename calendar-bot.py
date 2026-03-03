import utils
import telebot
import schedule
import datetime
import time
import traceback

from wrapper import functions, callbacks
from model import root as model_root
from model import meeting as model_meeting
from model import meeting_daily as model_meeting_daily
from model import meeting_weekly as model_meeting_weekly
from model import meeting_weekly_double as model_meeting_weekly_double

from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class BotExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        stack_trace = traceback.format_exc()
        print('--- Error in bot trace start ---')
        print(stack_trace)
        print('--- Error in bot trace end ---')
        return True


bot = telebot.TeleBot(model_root.select_token(), exception_handler=BotExceptionHandler())
print('Bot creating complete')

bot.set_my_commands([
    telebot.types.BotCommand('/start', 'Начало работы'),
    telebot.types.BotCommand('/meeting', 'Работа со встречами'),
    telebot.types.BotCommand('/admin', 'Управление')
])
print('Bot commands setting complete')

functions_admin = functions.AdminFunctions(bot)
functions_meeting = functions.MeetingFunctions(bot)
callbacks_meeting = callbacks.MeetingCallbackHandlers(functions_meeting)
callbacks_admin = callbacks.AdminCallbackHandlers(functions_admin)

COMMANDS_MEETING = {
    1: {
        'name': 'Добавить встречу',
        'function': functions_meeting.add
    },
    2: {
        'name': 'Удалить встречу',
        'function': functions_meeting.delete
    },
    3: {
        'name': 'Показать встречи',
        'function': functions_meeting.show
    }
}

COMMANDS_ADMIN = {
    4: {
        'name': 'Просмотр пользователей',
        'function': functions_admin.show_users
    },
    5: {
        'name': 'Просмотр логов',
        'function': functions_admin.logs
    }
}


# region root commands
@bot.message_handler(commands=['start'])
def start(message):
    model_root.upsert_chat(message.chat.id, message.chat.username, message.chat.title)
    bot.send_message(message.chat.id, 'Все отлично! Можно работать 👌')


@bot.message_handler(commands=['meeting'])
def meeting(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 6
    for key, value in COMMANDS_MEETING.items():
        markup.add(InlineKeyboardButton(text=value['name'], callback_data=f'command_{key}'))
    functions.add_cancel_button(markup)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(commands=['admin'])
def admin(message):
    if model_root.is_super_user(message.from_user.username):
        markup = InlineKeyboardMarkup()
        markup.row_width = 6
        for key, value in COMMANDS_ADMIN.items():
            markup.add(InlineKeyboardButton(text=value['name'], callback_data=f'command_{key}'))
        functions.add_cancel_button(markup)
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Отказано 🔒')


# endregion

# region root handlers
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


# endregion

# region callbacks from functions
@bot.callback_query_handler(func=lambda call: call.data.startswith('get_log_file'))
def get_log_file_callback_handler(call):
    callbacks_admin.get_logs_file(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('get_log_text'))
def get_log_text_callback_handler(call):
    callbacks_admin.get_logs_text(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('show_meeting_group_id'))
def show_meeting_group_id_callback_handler(call):
    callbacks_meeting.show_meeting_group_id_callback_handler(call, 'show_meeting_group_id')


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_meeting_group_id'))
def add_meeting_group_id_callback_handler(call):
    callbacks_meeting.add_meeting_group_id_callback_handler(call, 'add_meeting_group_id')


@bot.callback_query_handler(func=lambda call: call.data.startswith('date_meeting_group_id'))
def meeting_calendar_callback_handler(call):
    callbacks_meeting.add_meeting_date_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_meeting_regular_flg'))
def add_meeting_callback_handler(call):
    callbacks_meeting.add_meeting_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_meeting_group_id'))
def delete_meeting_group_id_callback_handler(call):
    callbacks_meeting.delete_meeting_group_id_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_meeting_id'))
def delete_meeting_id_callback_handler(call):
    callbacks_meeting.delete_meeting_id_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_meeting_regular_flg'))
def delete_meeting_group_id_callback_handler(call):
    callbacks_meeting.add_meeting_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('meeting_schedule'))
def meeting_schedule_callback_handler(call):
    callbacks_meeting.meeting_schedule_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('day_meeting_group_id'))
def meeting_day_callback_handler(call):
    callbacks_meeting.meeting_day_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('week_period_meeting_group_id'))
def meeting_week_period_callback_handler(call):
    callbacks_meeting.meeting_week_period_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel'))
def cancel_callback_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)


# endregion

# region scheduling
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            print(f'Error in scheduler: {str(ex)}')
            return None

    return wrapper


@handle_exceptions
def check_meetings_by_notification_day():
    meetings = model_meeting.select_meetings_for_notify_by_day()
    meetings_to_notify = list(filter(lambda m_: utils.is_date_tomorrow(m_.date_time), meetings))
    for m in meetings_to_notify:
        bot.send_message(m.chat_id, m.get_notify_text())
        model_meeting.update_meeting_notify_flag_day(m.id_)


@handle_exceptions
def check_meetings_by_notification_min():
    meetings = model_meeting.select_meetings_for_notify_by_min()
    meetings_to_notify = list(
        filter(lambda m_: utils.is_datetime_delta_passed_minutes(m_.date_time, int(m_.notify_lag_min)), meetings)
    )
    for m in meetings_to_notify:
        bot.send_message(m.chat_id, m.get_notify_text())
        model_meeting.update_meeting_notify_flag_min(m.id_)


@handle_exceptions
def check_meetings_daily():
    meetings = model_meeting_daily.select_meetings_daily_not_notified()
    meetings_to_notify = list(
        filter(lambda m_: utils.is_current_day_working() and
                          utils.is_time_delta_passed_minutes(m_.time_, int(m_.notify_lag_min)), meetings)
    )
    for m in meetings_to_notify:
        bot.send_message(m.chat_id, m.get_notify_text())
        model_meeting_daily.update_meetings_daily(m.id_)


@handle_exceptions
def check_meetings_weekly():
    meetings = model_meeting_weekly.select_meetings_weekly_not_notified()
    meetings_to_notify = list(
        filter(
            lambda m_: utils.is_time_delta_passed_minutes(m_.time_, int(m_.notify_lag_min)) and
                       datetime.datetime.now().isoweekday() == m_.day,
            meetings
        )
    )
    for m in meetings_to_notify:
        bot.send_message(m.chat_id, m.get_notify_text())
        model_meeting_weekly.update_meetings_weekly(m.id_)


@handle_exceptions
def check_meetings_weekly_double():
    meetings = model_meeting_weekly_double.select_meetings_weekly_double_not_notified()
    meetings_to_notify = list(
        filter(
            lambda m_: utils.is_current_week_even() == m_.is_even and
                       utils.is_time_delta_passed_minutes(m_.time_, int(m_.notify_lag_min)) and
                       datetime.datetime.now().isoweekday() == m_.day,
            meetings
        )
    )
    for m in meetings_to_notify:
        bot.send_message(m.chat_id, m.get_notify_text())
        model_meeting_weekly_double.update_meetings_weekly_double(m.id_)


@handle_exceptions
def backup_meetings_daily():
    model_meeting_daily.backup_meetings_daily()
    model_meeting_weekly.backup_meetings_weekly()
    model_meeting_weekly_double.backup_meetings_weekly_double()


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at('17:00').do(check_meetings_by_notification_day)
schedule.every().day.at('00:00').do(backup_meetings_daily)
schedule.every(1).minute.do(check_meetings_by_notification_min)
schedule.every(1).minute.do(check_meetings_daily)
schedule.every(1).minute.do(check_meetings_weekly)
schedule.every(1).minute.do(check_meetings_weekly_double)
Thread(target=run_schedule).start()

# endregion


updates = bot.get_updates()
if updates:
    last_update_id = updates[-1].update_id
    bot.get_updates(offset=last_update_id + 1)

bot.polling(none_stop=True, interval=0, skip_pending=True)
