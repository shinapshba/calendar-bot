import datetime
import re
import model
import utils

from dto import Meeting, MeetingDaily, MeetingWeekly, MeetingWeeklyDouble

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE

calendar = Calendar(language=RUSSIAN_LANGUAGE)
callback_add = CallbackData('date_meeting', 'action', 'year', 'month', 'day')


def raise_error(bot, chat_id, text):
    bot.send_message(chat_id, text)
    raise Exception(text)


def add_cancel_button(markup):
    markup.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))


def get_common_chats(bot, call):
    chat_ides = list(map(lambda c: c.chat_id, model.select_all_chats()))
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


class AdminFunctions:
    def __init__(self, bot):
        self.bot = bot

    def show_users(self, call):
        chats = model.select_all_chats()
        text = '\n'.join(sorted(list(map(lambda c: c.to_string(), chats))))
        if len(text) == 0:
            self.bot.send_message(call.message.chat.id, 'Список пользователей пуст')
            return
        self.bot.send_message(call.message.chat.id, text)


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
            meetings = model.select_meetings_for_chats(common_chat_ides)
            future_meetings = list(filter(lambda m: utils.is_in_future(m.date_time), meetings))
            meetings_daily = model.select_meetings_daily_for_chats(common_chat_ides)
            meetings_weekly = model.select_meetings_weekly_for_chats(common_chat_ides)
            meetings_weekly_double = model.select_meetings_weekly_double_for_chats(common_chat_ides)
        else:
            meetings = model.select_meetings(meeting_chat_id)
            future_meetings = list(filter(lambda m: utils.is_in_future(m.date_time), meetings))
            meetings_daily = model.select_meetings_daily(meeting_chat_id)
            meetings_weekly = model.select_meetings_weekly(meeting_chat_id)
            meetings_weekly_double = model.select_meetings_weekly_double(meeting_chat_id)

        if len(future_meetings) + len(meetings_daily) + len(meetings_weekly) + len(meetings_weekly_double) == 0:
            self.bot.send_message(call.message.chat.id, 'Нет встреч для этого чата 💅')
            return
        text = 'Встречи:\n'
        if call.message.chat.type == 'private':
            text += '\n'.join(list(map(lambda fm: f' * {fm.get_view_with_chat_title()}', future_meetings)))
            text += '\n'.join(list(map(lambda md: f' * {md.get_view_with_chat_title()}', meetings_daily)))
            text += '\n'.join(list(map(lambda mw: f' * {mw.get_view_with_chat_title()}', meetings_weekly)))
            text += '\n'.join(list(map(lambda mwd: f' * {mwd.get_view_with_chat_title()}', meetings_weekly_double)))
        else:
            text += '\n'.join(list(map(lambda fm: f' * {fm.get_view_short()}', future_meetings)))
            text += '\n'.join(list(map(lambda md: f' * {md.get_view_short()}', meetings_daily)))
            text += '\n'.join(list(map(lambda mw: f' * {mw.get_view_short()}', meetings_weekly)))
            text += '\n'.join(list(map(lambda mwd: f' * {mwd.get_view_short()}', meetings_weekly_double)))
        self.bot.send_message(call.message.chat.id, text)

    def delete(self, call):
        if call.message.chat.type != 'private':
            self.delete_(call.message, call.message.chat.id, call.from_user.username)
        else:
            reply_by_common_chats_markup(self.bot, call, 'delete_meeting_group_id')

    def delete_(self, message, meeting_chat_id, username):
        meetings = model.select_meetings_by_username(meeting_chat_id, username)
        future_meetings = list(filter(lambda m_: utils.is_in_future(m_.date_time), meetings))
        meetings_daily = model.select_meetings_daily_by_username(meeting_chat_id, username)
        meetings_weekly = model.select_meetings_weekly_by_username(meeting_chat_id, username)
        meetings_weekly_double = model.select_meetings_weekly_double_by_username(meeting_chat_id, username)
        if len(future_meetings) + len(meetings_daily) + len(meetings_weekly) + len(meetings_weekly_double) == 0:
            self.bot.send_message(message.chat.id, 'Нет доступных к удалению встреч 💅')
            return
        markup = InlineKeyboardMarkup()
        markup.row_width = 6
        for md in meetings_daily:
            markup.add(InlineKeyboardButton(text=md.get_short_view(),
                                            callback_data=f'delete_meeting_id_daily{md.id_}'))
        for mw in meetings_weekly:
            markup.add(InlineKeyboardButton(text=mw.get_short_view(),
                                            callback_data=f'delete_meeting_id_weekly{mw.id_}'))
        for mwd in meetings_weekly_double:
            markup.add(InlineKeyboardButton(text=mwd.get_short_view(),
                                            callback_data=f'delete_meeting_id_doubleweekly{mwd.id_}'))
        for m in future_meetings:
            markup.add(InlineKeyboardButton(text=m.get_short_view(),
                                            callback_data=f'delete_meeting_id{m.id_}'))
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'Выберите встречу', reply_markup=markup)

    def delete__(self, message, meeting_id):
        if '_daily' in meeting_id:
            model.delete_meeting_daily(meeting_id.replace('_daily', ''))
        elif '_weekly' in meeting_id:
            model.delete_meeting_weekly(meeting_id.replace('_weekly', ''))
        elif '_doubleweekly' in meeting_id:
            model.delete_meeting_weekly_double(meeting_id.replace('_doubleweekly', ''))
        else:
            model.delete_meeting(meeting_id)
        self.bot.send_message(message.chat.id, 'Удалил ✅')

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
        markup.add(InlineKeyboardButton(text='Каждые две недели',
                                        callback_data=f'meeting_schedule_doubleweekly_{meeting_chat_id}'))
        add_cancel_button(markup)
        self.bot.send_message(message.chat.id, 'Выберите регулярность', reply_markup=markup)

    def add_non_regular(self, message, meeting_chat_id):
        now = datetime.datetime.now()
        self.bot.send_message(
            message.chat.id, 'Выберите дату',
            reply_markup=calendar.create_calendar(name=f'date_meeting_group_id{meeting_chat_id}',
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

    def request_time_handler(self, message, **kwargs):
        text = message.text.strip()
        if re.fullmatch('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text) is not None:
            time_ = text
        elif str.isdigit(text):
            if int(text) > 23:
                raise_error(self.bot, message.chat.id, 'Час должен быть в периоде [0, 23]')
            time_ = f'{text}:00'
        else:
            raise_error(self.bot, message.chat.id, 'Неверный формат времени. '
                                                   'Поддерживаемые форматы:\n* <часы>\n* <часы>:<минуты>')
            return
        if 'schedule' not in kwargs:
            if datetime.datetime.combine(
                    date=kwargs['date'], time=datetime.datetime.strptime(time_, '%H:%M').time()
            ) < datetime.datetime.now():
                raise_error(self.bot, message.chat.id, 'Нельзя запланировать на прошедшее время 😐')
        kwargs['time'] = time_
        self.bot.send_message(message.chat.id, text=f'Место?')
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.__request_url_handler, **kwargs)

    def __request_url_handler(self, message, **kwargs):
        self.bot.send_message(chat_id=message.chat.id, text='Описание?')
        kwargs['place'] = message.text.strip()
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.__request_description_handler, **kwargs)

    def __request_description_handler(self, message, **kwargs):
        self.bot.send_message(chat_id=message.chat.id, text='За сколько минут оповестить?')
        kwargs['description'] = message.text.strip()
        self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.__request_min_for_notify, **kwargs)

    def __request_min_for_notify(self, message, **kwargs):
        if not str(message.text).isdigit() or int(message.text) == 0:
            raise_error(self.bot, message.chat.id, 'Нужно было ввести целое положительное чисто, больше 0')
        kwargs['notify_lag_min'] = message.text
        self.__create_meeting(message, **kwargs)

    def __create_meeting(self, message, **kwargs):
        meeting_chat = self.bot.get_chat(kwargs['meeting_chat_id'])
        if meeting_chat.type == 'private':
            chat_title = 'Личная'
        else:
            chat_title = meeting_chat.title
        if 'schedule' not in kwargs:
            model.insert_meeting(kwargs['meeting_chat_id'], chat_title, kwargs['username'], kwargs['place'],
                                 kwargs['description'], kwargs['notify_lag_min'],
                                 f'{kwargs["date"]} {kwargs["time"]}')
            self.bot.send_message(kwargs['meeting_chat_id'], Meeting.get_added_text(kwargs))
        elif kwargs['schedule'] == 'daily':
            model.insert_meeting_daily(kwargs['meeting_chat_id'], chat_title, kwargs['username'], kwargs['place'],
                                       kwargs['description'], kwargs['notify_lag_min'], kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingDaily.get_added_text(kwargs))
        elif kwargs['schedule'] == 'weekly':
            model.insert_meeting_weekly(kwargs['meeting_chat_id'], chat_title, kwargs['username'], kwargs['place'],
                                        kwargs['description'], kwargs['notify_lag_min'], kwargs['day'], kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingWeekly.get_added_text(kwargs))
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
            model.insert_meeting_weekly_double(kwargs['meeting_chat_id'], chat_title, kwargs['username'],
                                               kwargs['place'], kwargs['description'], kwargs['notify_lag_min'],
                                               is_even, kwargs['day'], kwargs['time'])
            self.bot.send_message(kwargs['meeting_chat_id'], MeetingWeeklyDouble.get_added_text(is_even, kwargs))
        if message.chat.type == 'private':
            self.bot.send_message(message.chat.id, text=f'Запланировал ✅')
