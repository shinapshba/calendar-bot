import datetime
import re

from wrapper.functions import MeetingFunctions
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE

calendar = Calendar(language=RUSSIAN_LANGUAGE)
callback_add = CallbackData('date_meeting', 'action', 'year', 'month', 'day')


class MeetingCallbackHandlers:
    def __init__(self, meeting_functions: MeetingFunctions):
        self.meeting_functions = meeting_functions
        self.bot = meeting_functions.bot

    def show_meeting_group_id_callback_handler(self, call, prefix):
        meeting_chat_id = call.data.replace(prefix, '')
        self.meeting_functions.show_(call, meeting_chat_id)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def add_meeting_date_callback_handler(self, call):
        name, action, year, month, day = call.data.split(callback_add.sep)
        date_ = calendar.calendar_query_handler(
            bot=self.bot, call=call, name=name, action=action, year=year, month=month, day=day  # noqa
        )
        if action == 'DAY':
            date_ = date_.date()
            if date_ < datetime.date.today():
                self.bot.send_message(call.message.chat.id, 'Нельзя запланировать на прошедшую дату 😐')
            else:
                self.bot.send_message(call.message.chat.id, 'Время? (HH:mm)')
                kwargs = {'date': date_,
                          'meeting_chat_id': name.replace('date_meeting_group_id', ''),
                          'username': call.from_user.username}
                self.bot.register_next_step_handler_by_chat_id(
                    call.message.chat.id, self.meeting_functions.request_time_handler, **kwargs
                )

    def add_meeting_group_id_callback_handler(self, call, prefix):
        meeting_chat_id = call.data.replace(prefix, '')
        self.meeting_functions.add_(call.message, meeting_chat_id)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def add_meeting_callback_handler(self, call):
        pattern = r'add_meeting_regular_flg(\d)_(.*)'
        match = re.match(pattern, call.data)
        is_regular = bool(int(match.group(1)))
        meeting_chat_id = match.group(2)
        if is_regular:
            self.meeting_functions.add_regular(call.message, meeting_chat_id)
        else:
            self.meeting_functions.add_non_regular(call.message, meeting_chat_id)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def delete_meeting_group_id_callback_handler(self, call):
        meeting_chat_id = call.data.replace('delete_meeting_group_id', '')
        self.meeting_functions.delete_(call.message, meeting_chat_id, call.from_user.username)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def delete_meeting_id_callback_handler(self, call):
        meeting_id = call.data.replace('delete_meeting_id', '')
        self.meeting_functions.delete__(call.message, meeting_id)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def meeting_schedule_callback_handler(self, call):
        schedule = call.data.replace('meeting_schedule_', '').split('_')[0]
        meeting_chat_id = call.data.split('_')[3]
        kwargs = {'schedule': schedule, 'meeting_chat_id': meeting_chat_id, 'username': call.from_user.username}
        if schedule == 'daily':
            self.bot.send_message(call.message.chat.id, 'Время? (HH:mm)')
            self.bot.register_next_step_handler_by_chat_id(
                call.message.chat.id, self.meeting_functions.request_time_handler, **kwargs
            )
        elif schedule == 'weekly':
            self.meeting_functions.request_week_day(call.message, meeting_chat_id)
        elif schedule == 'monthly':
            kwargs = {'schedule': schedule, 'meeting_chat_id': meeting_chat_id, 'username': call.from_user.username}
            self.bot.send_message(call.message.chat.id, 'Число?')
            self.bot.register_next_step_handler_by_chat_id(
                call.message.chat.id, self.meeting_functions.request_day_of_month, **kwargs
            )
        elif schedule == 'doubleweekly':
            self.meeting_functions.request_week_period(call.message, meeting_chat_id)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def meeting_day_callback_handler(self, call):
        pattern = r'day_meeting_group_id_(\d)_(\d)_(.*)'
        match = re.match(pattern, call.data)
        week_period = int(match.group(1))
        day = int(match.group(2))
        meeting_chat_id = match.group(3)
        if week_period == 0:
            schedule = 'weekly'
        else:
            schedule = 'doubleweekly'
        kwargs = {
            'schedule': schedule,
            'period': week_period,
            'meeting_chat_id': meeting_chat_id,
            'username': call.from_user.username,
            'day': day
        }
        self.bot.send_message(call.message.chat.id, 'Время? (HH:mm)')
        self.bot.register_next_step_handler_by_chat_id(
            call.message.chat.id, self.meeting_functions.request_time_handler, **kwargs
        )
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    def meeting_week_period_callback_handler(self, call):
        pattern = r'week_period_meeting_group_id_(\d)_(.*)'
        match = re.match(pattern, call.data)
        period = int(match.group(1))
        meeting_chat_id = match.group(2)
        self.meeting_functions.request_week_day(call.message, meeting_chat_id, period)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)
