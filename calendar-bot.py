import utils
import telebot
import schedule
import datetime
import time
import traceback
import os

from wrapper import functions, callbacks
from functions_dict import FunctionsDict
from model import root as model_root
from model import meeting as model_meeting
from model import meeting_daily as model_meeting_daily
from model import meeting_weekly as model_meeting_weekly
from model import meeting_monthly as model_meeting_monthly
from model import meeting_weekly_double as model_meeting_weekly_double
from wrapper.functions import ProductionCalendarFunctions, MeetingFunctions, AdminFunctions
from production_calendar import excel as p_excel
from production_calendar import dto as p_dto

from threading import Thread
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats


class BotExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        print(f'\n{utils.get_current_datetime()} Error in bot')
        print('--- Stack trace start ---')
        print(str(traceback.format_exc()).strip('\n'))
        print('--- Stack trace end ---')
        return True


commands_default = [
    BotCommand('/start', 'Начало работы'),
    BotCommand('/meeting', 'Работа со встречами'),
    BotCommand('/production', 'Производственный календарь')
]

commands_admin = [
    BotCommand('/admin', 'Управление')
]

apihelper.API_URL = model_root.select_proxy() + '{0}/{1}'
bot = telebot.TeleBot(model_root.select_token(), exception_handler=BotExceptionHandler())
bot.delete_my_commands()
bot.set_my_commands(commands=commands_default, scope=BotCommandScopeDefault())
bot.set_my_commands(commands=commands_default + commands_admin, scope=BotCommandScopeAllPrivateChats())

functions_admin = AdminFunctions(bot)
functions_meeting = MeetingFunctions(bot)
functions_production_calendar = ProductionCalendarFunctions(bot, model_root.select_production_calendar_token())
functions_dict = FunctionsDict(bot, functions_admin, functions_meeting)

callbacks_meeting = callbacks.MeetingCallbackHandlers(functions_meeting)
callbacks_admin = callbacks.AdminCallbackHandlers(functions_admin)

COMMANDS_MEETING = functions_dict.get_commands_meeting()
COMMANDS_ADMIN = functions_dict.get_commands_admin()


# region root commands
@bot.message_handler(commands=['start'])
def start(message):
    model_root.upsert_chat(message.chat.id, message.chat.username, message.chat.title)
    bot.send_message(message.chat.id, 'Все отлично! Можно работать 👌', reply_markup=functions.menu)


@bot.message_handler(commands=['meeting'])
@bot.message_handler(func=lambda message: message.chat.type == 'private' and str(message.text) == 'Встречи 🗣️')
def meeting(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 6
    for key, value in COMMANDS_MEETING.items():
        markup.add(InlineKeyboardButton(text=value['name'], callback_data=f'command_{key}'))
    functions.add_cancel_button(markup)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(commands=['admin'])
@bot.message_handler(func=lambda message: message.chat.type == 'private' and str(message.text) == 'Управление ⚙️')
def admin(message):
    if not model_root.is_super_user(message.from_user.username):
        bot.send_message(message.chat.id, 'Отказано 🔒')
        return
    markup = InlineKeyboardMarkup()
    markup.row_width = 6
    for key, value in COMMANDS_ADMIN.items():
        markup.add(InlineKeyboardButton(text=value['name'], callback_data=f'command_{key}'))
    functions.add_cancel_button(markup)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(commands=['production'])
@bot.message_handler(func=lambda message: message.chat.type == 'private' and
                                          str(message.text) == 'Производственный календарь 📅')
def production(message):
    def _refresh_files():
        bot.send_message(message.chat.id, 'Необходимо обновить файлы производственного календаря, '
                                          'запускаю обновление...')
        functions_production_calendar.update_production_calendar_files(message)

    if message.chat.type != 'private':
        return

    files = {
        'Неделя.xlsx': os.path.join(p_excel.FILES_DIR, p_dto.Week.FILE_NAME),
        'Месяц.xlsx': os.path.join(p_excel.FILES_DIR, p_dto.Month.FILE_NAME),
        'Квартал.xlsx': os.path.join(p_excel.FILES_DIR, p_dto.Quarter.FILE_NAME),
        'Год.xlsx': os.path.join(p_excel.FILES_DIR, p_dto.Year.FILE_NAME)
    }
    files = {key: os.path.abspath(path) for key, path in files.items()}  # noqa

    do_refresh = False
    if os.path.exists(p_excel.FILES_DIR):
        today = datetime.datetime.today().date()
        for name in files:
            if not os.path.exists(files[name]):
                do_refresh = True
                break
            last_modified = os.path.getmtime(files[name])
            last_modified_date = datetime.datetime.fromtimestamp(last_modified).date()
            if last_modified_date < today:
                do_refresh = True
                break
    else:
        do_refresh = True
    if do_refresh:
        try:
            _refresh_files()
        except Exception as ex:
            bot.send_message(message.chat.id, 'Ошибка при попытке обновить производственный календарь ❌')
            raise ex

    for file_name in files:
        file_path_abs = os.path.abspath(files[file_name])
        with open(file_path_abs, 'rb') as file:
            bot.send_document(message.chat.id, file, visible_file_name=file_name)
    bot.send_message(message.chat.id, 'Все файлы календаря отправлены ✅', reply_markup=functions.menu)


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


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_notifies_chat_id'))
def delete_notifies_by_chat_id_callback_handler(call):
    callbacks_admin.delete_notifies(call, 'delete_notifies_chat_id')


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel'))
def cancel_callback_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)


# endregion

# region scheduling
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:  # noqa
            print(f'\n{utils.get_current_datetime()} Error in scheduler')
            print('--- Stack trace start ---')
            print(str(traceback.format_exc()).strip('\n'))
            print('--- Stack trace end ---')
            return None

    return wrapper


@handle_exceptions
def check_meetings_by_notification_day():
    is_day_off = model_root.select_is_today_day_off()
    meetings = model_meeting.select_meetings_for_notify_by_day()
    meetings_to_notify = list(filter(lambda m_: utils.is_date_tomorrow(m_.date_time), meetings))
    for m in meetings_to_notify:
        bot.send_message(m.chat_id, m.get_notify_text(), parse_mode='HTML', disable_notification=is_day_off)
        model_meeting.update_meeting_notify_flag_day(m.id_)


@handle_exceptions
def check_meetings_by_notification_min():
    is_day_off = model_root.select_is_today_day_off()
    meetings = model_meeting.select_meetings_for_notify_by_min()
    meetings_to_notify = list(
        filter(lambda m_: utils.is_datetime_delta_passed_minutes(m_.date_time, int(m_.notify_lag_min)), meetings)
    )
    for m in meetings_to_notify:
        sent_message = bot.send_message(m.chat_id, m.get_notify_text(), parse_mode='HTML',
                                        disable_notification=is_day_off)
        model_meeting.update_meeting_notify_flag_min(m.id_)
        model_root.insert_sent_notify(sent_message.chat.id, sent_message.message_id)


@handle_exceptions
def check_meetings_daily():
    is_day_off = model_root.select_is_today_day_off()
    meetings = model_meeting_daily.select_meetings_daily_not_notified()
    meetings_to_notify = list(
        filter(lambda m_: utils.is_current_day_working() and
                          utils.is_time_delta_passed_minutes(m_.time_, int(m_.notify_lag_min)), meetings)
    )
    for m in meetings_to_notify:
        sent_message = bot.send_message(m.chat_id, m.get_notify_text(), parse_mode='HTML',
                                        disable_notification=is_day_off)
        model_meeting_daily.update_meetings_daily(m.id_)
        model_root.insert_sent_notify(sent_message.chat.id, sent_message.message_id)


@handle_exceptions
def check_meetings_weekly():
    is_day_off = model_root.select_is_today_day_off()
    meetings = model_meeting_weekly.select_meetings_weekly_not_notified()
    meetings_to_notify = list(
        filter(
            lambda m_: utils.is_time_delta_passed_minutes(m_.time_, int(m_.notify_lag_min)) and
                       datetime.datetime.now().isoweekday() == m_.day,
            meetings
        )
    )
    for m in meetings_to_notify:
        sent_message = bot.send_message(m.chat_id, m.get_notify_text(), parse_mode='HTML',
                                        disable_notification=is_day_off)
        model_meeting_weekly.update_meetings_weekly(m.id_)
        model_root.insert_sent_notify(sent_message.chat.id, sent_message.message_id)


@handle_exceptions
def check_meetings_monthly():
    is_day_off = model_root.select_is_today_day_off()
    meetings = model_meeting_monthly.select_meetings_monthly_not_notified()
    meetings_to_notify = list(
        filter(
            lambda m_: utils.is_time_delta_passed_minutes(m_.time_, int(m_.notify_lag_min)) and
                       utils.is_today_is_day_of_month(m_.day_of_month),
            meetings
        )
    )
    for m in meetings_to_notify:
        sent_message = bot.send_message(m.chat_id, m.get_notify_text(), parse_mode='HTML',
                                        disable_notification=is_day_off)
        model_meeting_monthly.update_meetings_monthly(m.id_)
        model_root.insert_sent_notify(sent_message.chat.id, sent_message.message_id)


@handle_exceptions
def check_meetings_weekly_double():
    is_day_off = model_root.select_is_today_day_off()
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
        sent_message = bot.send_message(m.chat_id, m.get_notify_text(), parse_mode='HTML',
                                        disable_notification=is_day_off)
        model_meeting_weekly_double.update_meetings_weekly_double(m.id_)
        model_root.insert_sent_notify(sent_message.chat.id, sent_message.message_id)


@handle_exceptions
def backup_meetings_daily():
    model_meeting_daily.backup_meetings_daily()
    model_meeting_weekly.backup_meetings_weekly()
    model_meeting_monthly.backup_meetings_monthly()
    model_meeting_weekly_double.backup_meetings_weekly_double()


@handle_exceptions
def delete_sent_notifies():
    sent_notifies = model_root.select_sent_notify()
    if sent_notifies is not None and len(sent_notifies) != 0:
        for notify in sent_notifies:
            try:
                bot.delete_message(notify.chat_id, notify.message_id)
                model_root.delete_sent_notify_by_chat_id_and_message_id(notify.chat_id, notify.message_id)
            except:  # noqa
                pass


@handle_exceptions
def update_production_calendar_files():
    functions_production_calendar.run_update_production_calendar_files()


@handle_exceptions
def set_is_today_day_off():
    pass


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at('17:00').do(check_meetings_by_notification_day)
schedule.every().day.at('00:00').do(backup_meetings_daily)
schedule.every().day.at('00:30').do(set_is_today_day_off)
schedule.every().day.at('01:00').do(delete_sent_notifies)
schedule.every(1).minute.do(check_meetings_by_notification_min)
schedule.every(1).minute.do(check_meetings_daily)
schedule.every(1).minute.do(check_meetings_weekly)
schedule.every(1).minute.do(check_meetings_monthly)
schedule.every(1).minute.do(check_meetings_weekly_double)
schedule.every().day.at('03:00').do(update_production_calendar_files)
Thread(target=run_schedule).start()

# endregion

if not os.path.exists('./tmp'):
    os.mkdir('./tmp')

updates = bot.get_updates()
if updates:
    last_update_id = updates[-1].update_id
    bot.get_updates(offset=last_update_id + 1)

bot.infinity_polling(none_stop=True, interval=0, skip_pending=True, timeout=60, long_polling_timeout=60)
