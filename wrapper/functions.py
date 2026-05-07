import datetime
import re
import utils
import html
import os
import threading

from model import root as m_root
from model import meeting as m_meeting
from model import meeting_daily as m_meeting_daily
from model import meeting_monthly as m_meeting_monthly
from model import meeting_weekly as m_meeting_weekly
from model import meeting_weekly_double as m_meeting_weekly_double
from dto import Meeting, MeetingDaily, MeetingWeekly, MeetingWeeklyDouble, MeetingMonthly
from integration.dto import Week, Month, Quarter, Year
from integration import excel

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE

calendar_meeting = Calendar(language=RUSSIAN_LANGUAGE)

# region utils
menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
menu.row('Встречи 🗣️', 'Управление ⚙️')
menu.row('Производственный календарь 📅')


def add_cancel_button(markup):
    markup.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))


def convert_message_to_html(message):
    text = message.text
    entities = message.entities
    if not text:
        return ""
    if not entities:
        return html.escape(text, quote=False)
    text = html.escape(text, quote=False)
    sorted_entities = sorted(entities, key=lambda e_: e_.offset, reverse=True)
    result = text
    for entity in sorted_entities:
        if entity.offset < 0 or entity.length <= 0:
            continue
        start = entity.offset
        end = entity.offset + entity.length
        if start >= len(result) or end > len(result):
            continue
        entity_text = result[start:end]
        if not entity_text:
            continue
        try:
            if entity.type == "bold":
                result = result[:start] + f"<b>{entity_text}</b>" + result[end:]
            elif entity.type == "italic":
                result = result[:start] + f"<i>{entity_text}</i>" + result[end:]
            elif entity.type == "underline":
                result = result[:start] + f"<u>{entity_text}</u>" + result[end:]
            elif entity.type == "strikethrough":
                result = result[:start] + f"<s>{entity_text}</s>" + result[end:]
            elif entity.type == "code":
                result = result[:start] + f"<code>{entity_text}</code>" + result[end:]
            elif entity.type == "pre":
                language = getattr(entity, 'language', '')
                if language:
                    safe_language = html.escape(language)
                    result = (result[:start] +
                              f"<pre><code class='language-{safe_language}'>{entity_text}</code></pre>" + result[end:])
                else:
                    result = result[:start] + f"<pre>{entity_text}</pre>" + result[end:]
            elif entity.type == "text_link":
                url = getattr(entity, 'url', '')
                if url:
                    safe_url = html.escape(url)
                    if safe_url.lower().startswith('javascript:'):
                        safe_url = '#'
                    result = result[:start] + f"<a href='{safe_url}'>{entity_text}</a>" + result[end:]
                else:
                    result = result[:start] + entity_text + result[end:]
            elif entity.type == "url":
                safe_url = html.escape(entity_text)
                if safe_url.lower().startswith('javascript:'):
                    safe_url = '#'
                result = result[:start] + f"<a href='{safe_url}'>{entity_text}</a>" + result[end:]
            elif entity.type == "mention":
                username = entity_text[1:]  # убираем @
                safe_username = html.escape(username)
                result = result[:start] + f"<a href='https://t.me/{safe_username}'>{entity_text}</a>" + result[end:]
            elif entity.type == "hashtag":
                result = result[:start] + f"<b>{entity_text}</b>" + result[end:]
            elif entity.type == "email":
                safe_email = html.escape(entity_text)
                result = result[:start] + f"<a href='mailto:{safe_email}'>{entity_text}</a>" + result[end:]
            elif entity.type == "phone_number":
                safe_phone = html.escape(entity_text)
                result = result[:start] + f"<a href='tel:{safe_phone}'>{entity_text}</a>" + result[end:]
            elif entity.type == "spoiler":
                result = result[:start] + f"<span class='tg-spoiler'>{entity_text}</span>" + result[end:]
            else:
                result = result[:start] + entity_text + result[end:]
        except Exception:  # noqa
            continue
    return result


def get_common_chats(bot, call):
    chat_ides = list(map(lambda c: c.chat_id, m_root.select_all_chats()))
    chats = list(map(lambda i: bot.get_chat(i), chat_ides))
    groups = list(filter(lambda c: c.type in ['group', 'supergroup'], chats))
    return list(filter(lambda group: bot.get_chat_member(group.id, call.from_user.id).status in
                                     ['creator', 'administrator', 'member'], groups))


def build_common_chats_markup(bot, call, markup_prefix):
    common_chats = get_common_chats(bot, call)
    markup = InlineKeyboardMarkup()
    markup.row_width = 6
    for chat in common_chats:
        markup.add(InlineKeyboardButton(text=str(chat.title), callback_data=f'{markup_prefix}{chat.id}'))
    return markup


def reply_by_common_chats_markup(bot, call, markup_prefix):
    markup = build_common_chats_markup(bot, call, markup_prefix)
    if call.message.chat.type == 'private':
        markup.add(InlineKeyboardButton(text='ЛС', callback_data=f'{markup_prefix}{call.message.chat.id}'))
    add_cancel_button(markup)
    bot.send_message(call.message.chat.id, 'Выберите чат', reply_markup=markup)


# endregion


class AdminFunctions:
    def __init__(self, bot):
        self.bot = bot

    LOG_FILE = './nohup.out'

    @staticmethod
    def __send_logs_file_async(bot, chat_id):
        if not os.path.exists(AdminFunctions.LOG_FILE):
            bot.send_message(chat_id, 'Файл логов не найден', reply_markup=menu)
            return
        if os.path.getsize(AdminFunctions.LOG_FILE) == 0:
            bot.send_message(chat_id, 'Файл логов пуст', reply_markup=menu)
            return
        with open(AdminFunctions.LOG_FILE, 'rb') as log_file:
            bot.send_document(chat_id, log_file, reply_markup=menu)

    def logs(self, call):
        thread = threading.Thread(target=AdminFunctions.__send_logs_file_async,
                                  args=(self.bot, call.message.chat.id))
        thread.daemon = True
        thread.start()

    def show_users(self, call):
        chats = m_root.select_all_chats()
        text = '\n'.join(sorted(list(map(lambda c: c.to_string(), chats))))
        if len(text) == 0:
            self.bot.send_message(call.message.chat.id, 'Список пользователей пуст', reply_markup=menu)
            return
        self.bot.send_message(call.message.chat.id, text, reply_markup=menu)


class MeetingFunctions:
    def __init__(self, bot):
        self.bot = bot

    def show(self, call):
        if call.message.chat.type != 'private':
            self.show_(call, call.message.chat.id)
        else:
            prefix = 'show_meeting_group_id'
            markup = build_common_chats_markup(self.bot, call, prefix)
            if call.message.chat.type == 'private':
                markup.row(
                    InlineKeyboardButton(text='Личные', callback_data=f'{prefix}{call.message.chat.id}'),
                    InlineKeyboardButton(text='Все', callback_data=f'{prefix}all')
                )
            add_cancel_button(markup)
            self.bot.send_message(call.message.chat.id, 'Выберите чат или опцию', reply_markup=markup)

    def show_(self, call, meeting_chat_id):
        if meeting_chat_id == 'all':
            common_chat_ides = list(map(lambda c: c.id, get_common_chats(self.bot, call)))
            common_chat_ides.append(call.message.chat.id)
            meetings = m_meeting.select_meetings_for_chats(common_chat_ides)
            future_meetings = list(filter(lambda m: utils.is_in_future(m.date_time), meetings))
            meetings_daily = m_meeting_daily.select_meetings_daily_for_chats(common_chat_ides)
            meetings_weekly = m_meeting_weekly.select_meetings_weekly_for_chats(common_chat_ides)
            meetings_monthly = m_meeting_monthly.select_meetings_monthly_for_chats(common_chat_ides)
            meetings_weekly_double = m_meeting_weekly_double.select_meetings_weekly_double_for_chats(common_chat_ides)
        else:
            meetings = m_meeting.select_meetings(meeting_chat_id)
            future_meetings = list(filter(lambda m: utils.is_in_future(m.date_time), meetings))
            meetings_daily = m_meeting_daily.select_meetings_daily(meeting_chat_id)
            meetings_weekly = m_meeting_weekly.select_meetings_weekly(meeting_chat_id)
            meetings_monthly = m_meeting_monthly.select_meetings_monthly(meeting_chat_id)
            meetings_weekly_double = m_meeting_weekly_double.select_meetings_weekly_double(meeting_chat_id)

        if (len(future_meetings) +
                len(meetings_daily) +
                len(meetings_weekly) +
                len(meetings_weekly_double) +
                len(meetings_monthly) == 0):
            self.bot.send_message(call.message.chat.id, 'Нет встреч 💅', reply_markup=menu)
            return

        meeting_views = []
        if call.message.chat.type == 'private':
            meeting_views += list(map(lambda fm: f' * {fm.get_view_with_chat_title()}', future_meetings))
            meeting_views += list(map(lambda md: f' * {md.get_view_with_chat_title()}', meetings_daily))
            meeting_views += list(map(lambda mw: f' * {mw.get_view_with_chat_title()}', meetings_weekly))
            meeting_views += list(map(lambda mm: f' * {mm.get_view_with_chat_title()}', meetings_monthly))
            meeting_views += list(map(lambda mwd: f' * {mwd.get_view_with_chat_title()}', meetings_weekly_double))
        else:
            meeting_views += list(map(lambda fm: f' * {fm.get_view_short()}', future_meetings))
            meeting_views += list(map(lambda md: f' * {md.get_view_short()}', meetings_daily))
            meeting_views += list(map(lambda mw: f' * {mw.get_view_short()}', meetings_weekly))
            meeting_views += list(map(lambda mm: f' * {mm.get_view_short()}', meetings_monthly))
            meeting_views += list(map(lambda mwd: f' * {mwd.get_view_short()}', meetings_weekly_double))
        meeting_views.sort()
        self.bot.send_message(call.message.chat.id, 'Встречи:\n' + '\n'.join(meeting_views), reply_markup=menu)

    def delete(self, call):
        if call.message.chat.type != 'private':
            self.delete_(call.message, call.message.chat.id, call.from_user.username)
        else:
            reply_by_common_chats_markup(self.bot, call, 'delete_meeting_group_id')

    def delete_(self, message, meeting_chat_id, username):
        meetings = m_meeting.select_meetings_by_username(meeting_chat_id, username)
        future_meetings = list(filter(lambda m_: utils.is_in_future(m_.date_time), meetings))
        meetings_daily = m_meeting_daily.select_meetings_daily_by_username(meeting_chat_id, username)
        meetings_weekly = m_meeting_weekly.select_meetings_weekly_by_username(meeting_chat_id, username)
        meetings_monthly = m_meeting_monthly.select_meetings_monthly_by_username(meeting_chat_id, username)
        meetings_weekly_double = m_meeting_weekly_double.select_meetings_weekly_double_by_username(meeting_chat_id,
                                                                                                   username)
        if (len(future_meetings) +
                len(meetings_daily) +
                len(meetings_weekly) +
                len(meetings_weekly_double) +
                len(meetings_monthly) == 0):
            self.bot.send_message(message.chat.id, 'Нет доступных к удалению встреч 💅', reply_markup=menu)
            return
        markup = InlineKeyboardMarkup()
        markup.row_width = 6

        def build_inline_button(meeting, prefix):
            return InlineKeyboardButton(text=meeting.get_view_short(), callback_data=f'{prefix}{meeting.id_}')

        for md in meetings_daily:
            markup.add(build_inline_button(md, 'delete_meeting_id_daily'))
        for mw in meetings_weekly:
            markup.add(build_inline_button(mw, 'delete_meeting_id_weekly'))
        for mm in meetings_monthly:
            markup.add(build_inline_button(mm, 'delete_meeting_id_monthly'))
        for mwd in meetings_weekly_double:
            markup.add(build_inline_button(mwd, 'delete_meeting_id_doubleweekly'))
        for m in future_meetings:
            markup.add(build_inline_button(m, 'delete_meeting_id'))
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'Выберите встречу', reply_markup=markup)

    def delete__(self, message, meeting_id):
        if '_daily' in meeting_id:
            m_meeting_daily.delete_meeting_daily(meeting_id.replace('_daily', ''))
        elif '_weekly' in meeting_id:
            m_meeting_weekly.delete_meeting_weekly(meeting_id.replace('_weekly', ''))
        elif '_monthly' in meeting_id:
            m_meeting_monthly.delete_meeting_monthly(meeting_id.replace('_monthly', ''))
        elif '_doubleweekly' in meeting_id:
            m_meeting_weekly_double.delete_meeting_weekly_double(meeting_id.replace('_doubleweekly', ''))
        else:
            m_meeting.delete_meeting(meeting_id)
        self.bot.send_message(message.chat.id, 'Удалил встречу ✅', reply_markup=menu)

    def add(self, call):
        if call.message.chat.type != 'private':
            self.add_(call.message, call.message.chat.id)
        else:
            reply_by_common_chats_markup(self.bot, call, 'add_meeting_group_id')

    def add_(self, message, meeting_chat_id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.row(
            InlineKeyboardButton(text='Да', callback_data=f'add_meeting_regular_flg1_{meeting_chat_id}'),
            InlineKeyboardButton(text='Нет', callback_data=f'add_meeting_regular_flg0_{meeting_chat_id}')
        )
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'Встреча регулярная?', reply_markup=markup)

    def add_regular(self, message, meeting_chat_id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton(text='Ежедневно', callback_data=f'meeting_schedule_daily_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Еженедельно', callback_data=f'meeting_schedule_weekly_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Ежемесячно', callback_data=f'meeting_schedule_monthly_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Каждые две недели',
                                        callback_data=f'meeting_schedule_doubleweekly_{meeting_chat_id}'))
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'Выберите регулярность', reply_markup=markup)

    def add_non_regular(self, message, meeting_chat_id):
        now = datetime.datetime.now()
        self.bot.send_message(
            message.chat.id, 'Выберите дату',
            reply_markup=calendar_meeting.create_calendar(name=f'date_meeting_group_id{meeting_chat_id}',
                                                          year=now.year, month=now.month)
        )

    def request_week_day(self, message, meeting_chat_id, week_period: int = 0):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton(text='Понедельник',
                                        callback_data=f'day_meeting_group_id_{week_period}_1_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Вторник',
                                        callback_data=f'day_meeting_group_id_{week_period}_2_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Среда',
                                        callback_data=f'day_meeting_group_id_{week_period}_3_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Четверг',
                                        callback_data=f'day_meeting_group_id_{week_period}_4_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Пятница',
                                        callback_data=f'day_meeting_group_id_{week_period}_5_{meeting_chat_id}'))
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'Выберите день', reply_markup=markup)

    def request_week_period(self, message, meeting_chat_id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton(text='С текущей',
                                        callback_data=f'week_period_meeting_group_id_1_{meeting_chat_id}'))
        markup.add(InlineKeyboardButton(text='Со следующей',
                                        callback_data=f'week_period_meeting_group_id_2_{meeting_chat_id}'))
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'начиная с какой недели?', reply_markup=markup)

    def request_day_of_month(self, message, **kwargs):
        text = message.text.strip()
        if re.fullmatch('^([1-9]|[12][0-9]|3[01])$', text) is None:
            self.bot.send_message(message.chat.id, 'Нужно было ввести число от 1 до 31 😐', reply_markup=menu)
            return
        kwargs['day_of_month'] = text
        self.bot.send_message(message.chat.id, 'Время? (HH:mm)')
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.request_time_handler, **kwargs)

    def request_time_handler(self, message, **kwargs):
        text = message.text.strip()
        if re.fullmatch('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text) is not None:
            time_ = text
        elif str.isdigit(text):
            if int(text) > 23:
                self.bot.send_message(message.chat.id, 'Час должен быть в периоде [0, 23]', reply_markup=menu)
                return
            time_ = f'{text}:00'
        else:
            self.bot.send_message(message.chat.id, 'Неверный формат времени. Поддерживаемые форматы:'
                                                   '\n* <часы>\n* <часы>:<минуты>', reply_markup=menu)
            return
        if 'schedule' not in kwargs:
            if datetime.datetime.combine(
                    date=kwargs['date'], time=datetime.datetime.strptime(time_, '%H:%M').time()
            ) < datetime.datetime.now():
                self.bot.send_message(message.chat.id, 'Нельзя запланировать на прошедшее время 😐', reply_markup=menu)
                return
        kwargs['time'] = time_
        self.bot.send_message(message.chat.id, text=f'Место?')
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.__request_url_handler, **kwargs)

    def __request_url_handler(self, message, **kwargs):
        self.bot.send_message(chat_id=message.chat.id, text='Описание?')
        kwargs['place'] = convert_message_to_html(message)
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.__request_description_handler, **kwargs)

    def __request_description_handler(self, message, **kwargs):
        self.bot.send_message(chat_id=message.chat.id, text='За сколько минут оповестить?')
        kwargs['description'] = convert_message_to_html(message)
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.__request_min_for_notify, **kwargs)

    def __request_min_for_notify(self, message, **kwargs):
        if not str(message.text).isdigit() or int(message.text) == 0:
            self.bot.send_message(message.chat.id, 'Нужно было ввести целое положительное чисто, больше 0',
                                  reply_markup=menu)
            return
        kwargs['notify_lag_min'] = message.text
        self.__create_meeting(message, **kwargs)

    def __create_meeting(self, message, **kwargs):
        meeting_chat = self.bot.get_chat(kwargs['meeting_chat_id'])
        if meeting_chat.type == 'private':
            chat_title = 'Личная'
        else:
            chat_title = meeting_chat.title
        if 'schedule' not in kwargs:
            m_meeting.insert_meeting(kwargs['meeting_chat_id'], chat_title, kwargs['username'], kwargs['place'],
                                     kwargs['description'], kwargs['notify_lag_min'],
                                     f'{kwargs["date"]} {kwargs["time"]}')
            self.bot.send_message(kwargs['meeting_chat_id'], Meeting.get_added_text(kwargs), parse_mode='HTML')
        elif kwargs['schedule'] == 'daily':
            m_meeting_daily.insert_meeting_daily(kwargs['meeting_chat_id'], chat_title, kwargs['username'],
                                                 kwargs['place'], kwargs['description'], kwargs['notify_lag_min'],
                                                 kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingDaily.get_added_text(kwargs), parse_mode='HTML')
        elif kwargs['schedule'] == 'weekly':
            m_meeting_weekly.insert_meeting_weekly(kwargs['meeting_chat_id'], chat_title, kwargs['username'],
                                                   kwargs['place'], kwargs['description'],
                                                   kwargs['notify_lag_min'], kwargs['day'], kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingWeekly.get_added_text(kwargs), parse_mode='HTML')
        elif kwargs['schedule'] == 'monthly':
            m_meeting_monthly.insert_meeting_monthly(kwargs['meeting_chat_id'], chat_title, kwargs['username'],
                                                     kwargs['place'], kwargs['description'],
                                                     kwargs['notify_lag_min'], kwargs['day_of_month'], kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingMonthly.get_added_text(kwargs), parse_mode='HTML')
        elif kwargs['schedule'] == 'doubleweekly':
            if utils.is_current_week_even():
                if int(kwargs['period']) == 1:
                    is_even = 1
                else:
                    is_even = 0
            else:
                if int(kwargs['period']) == 1:
                    is_even = 0
                else:
                    is_even = 1
            m_meeting_weekly_double.insert_meeting_weekly_double(kwargs['meeting_chat_id'], chat_title,
                                                                 kwargs['username'], kwargs['place'],
                                                                 kwargs['description'], kwargs['notify_lag_min'],
                                                                 is_even, kwargs['day'], kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingWeeklyDouble.get_added_text(is_even, kwargs),
                                  parse_mode='HTML')
        if message.chat.type == 'private':
            self.bot.send_message(message.chat.id, text=f'Запланировал ✅', reply_markup=menu)


class ProductionFunctions:
    def __init__(self, bot, production_calendar):
        self.production_calendar = production_calendar
        self.bot = bot

    def _safe_send(self, chat_id, file_name):
        try:
            with open(file_name, 'rb') as file:
                self.bot.send_document(chat_id, file, visible_file_name='Инфо.xlsx', reply_markup=menu)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def _handle_response(self, call, response):
        if response.status_code != 200:
            text = 'Ошибка от ресурса https://production-calendar.ru'
            self.bot.send_message(call.message.chat.id, text, reply_markup=menu)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            raise Exception(f'Response from {response.url}: {response.text}')

    def week(self, call):
        response = self.production_calendar.get_current_week()
        self._handle_response(call, response)
        week = Week.from_dict(response.json())
        file_name = excel.create_file_week(week)
        self._safe_send(call.message.chat.id, file_name)

    def month(self, call):
        response = self.production_calendar.get_current_month()
        self._handle_response(call, response)
        month = Month.from_dict(response.json())
        file_name = excel.create_file_month(month)
        self._safe_send(call.message.chat.id, file_name)

    def quarter(self, call):
        response = self.production_calendar.get_current_quarter()
        self._handle_response(call, response)
        quarter = Quarter.from_dict(response.json())
        file_name = excel.create_file_quarter(quarter)
        self._safe_send(call.message.chat.id, file_name)

    def year(self, call):
        response = self.production_calendar.get_current_year()
        self._handle_response(call, response)
        year = Year.from_dict(response.json())
        file_name = excel.create_file_year(year)
        self._safe_send(call.message.chat.id, file_name)
