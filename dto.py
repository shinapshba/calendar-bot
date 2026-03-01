class Chat:
    def __init__(self, chat_id, username, title):
        self.chat_id = chat_id
        self.username = username
        self.title = title

    def to_string(self):
        if self.username is not None:
            return f'Пользователь @{self.username}'
        return f'Чат "{self.title}"'


class Meeting:
    def __init__(self, id_, chat_id, chat_title, username, place, description, date_time, notify_lag_min,
                 is_notified_day, is_notified_min):
        self.id_ = id_
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.username = username
        self.place = place
        self.description = description
        self.date_time = date_time
        self.notify_lag_min = notify_lag_min
        self.is_notified_day = bool(int(is_notified_day))
        self.is_notified_min = bool(int(is_notified_min))

    @staticmethod
    def row_factory():
        return lambda cursor, row: Meeting(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
        )

    def get_notify_text(self):
        return (f'Напоминание о встрече 👀\n'
                f'Дата и время: {self.date_time}\n'
                f'Место: {self.place}\n'
                f'Описание: {self.description}\n\n'
                f'Directed by @{self.username}')

    @staticmethod
    def get_added_text(kwargs):
        return (f'Добавлена встреча 🌚\n'
                f'Дата и время: {kwargs["date"]} {kwargs["time"]}\n'
                f'Место: {kwargs["place"]}\n'
                f'Описание: {kwargs["description"]}\n\n'
                f'Directed by @{kwargs["username"]}')

    def get_view_with_chat_title(self):
        return f'{self.chat_title}. Одиночная - {self.date_time}'

    def get_view_short(self):
        return f'Одиночная, {self.date_time}'


class MeetingDaily:
    def __init__(self, id_, chat_id, chat_title, username, place, description, time_, notify_lag_min, is_notified):
        self.id_ = id_
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.username = username
        self.place = place
        self.description = description
        self.time_ = time_
        self.notify_lag_min = notify_lag_min
        self.is_notified = bool(int(is_notified))

    @staticmethod
    def row_factory():
        return lambda cursor, row: MeetingDaily(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

    def get_notify_text(self):
        return (f'Напоминание о встрече 👀\n'
                f'Время: {self.time_}\n'
                f'Место: {self.place}\n'
                f'Описание: {self.description}\n\n'
                f'Directed by @{self.username}')

    @staticmethod
    def get_added_text(kwargs):
        return (f'Добавлена встреча 🐳\n'
                f'Ежедневно: {kwargs["time"]}\n'
                f'Место: {kwargs["place"]}\n'
                f'Описание: {kwargs["description"]}\n'
                f'Лаг оповещения в минутах: {kwargs["notify_lag_min"]}\n\n'
                f'Directed by @{kwargs["username"]}')

    def get_view_with_chat_title(self):
        return f'{self.chat_title}. Ежедневная, в {self.time_}'

    def get_view_short(self):
        return f'Ежедневная, в {self.time_}'


class MeetingWeekly:
    def __init__(self, id_, chat_id, chat_title, username, place, description, day, time_, notify_lag_min, is_notified):
        self.id_ = id_
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.username = username
        self.place = place
        self.description = description
        self.day = int(day)
        self.time_ = time_
        self.notify_lag_min = notify_lag_min
        self.is_notified = bool(int(is_notified))

    @staticmethod
    def row_factory():
        return lambda cursor, row: MeetingWeekly(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
        )

    def get_notify_text(self):
        return (f'Напоминание встрече 👀\n'
                f'Время: {self.time_}\n'
                f'Место: {self.place}\n'
                f'Описание: {self.description}\n\n'
                f'Directed by @{self.username}')

    @staticmethod
    def define_day_string(day):
        return {
            1: 'По понедельникам',
            2: 'По вторникам',
            3: 'По средам',
            4: 'По четвергам',
            5: 'По пятницам'
        }[day]

    def get_day_string(self):
        return MeetingWeekly.define_day_string(self.day)

    @staticmethod
    def get_added_text(kwargs):
        return (f'Добавлена встреча 👻\n'
                f'{MeetingWeekly.define_day_string(int(kwargs["day"]))}, в {kwargs["time"]}\n'
                f'Место: {kwargs["place"]}\n'
                f'Описание: {kwargs["description"]}\n'
                f'Лаг оповещения в минутах: {kwargs["notify_lag_min"]}\n\n'
                f'Directed by @{kwargs["username"]}')

    def get_view_with_chat_title(self):
        return f'{self.chat_title}. {self.get_day_string()}, в {self.time_}'

    def get_view_short(self):
        return f'{self.get_day_string()}, в {self.time_}'


class MeetingWeeklyDouble:
    def __init__(self, id_, chat_id, chat_title, username, place, description, is_even, day, time_,
                 notify_lag_min, is_notified):
        self.id_ = id_
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.username = username
        self.place = place
        self.description = description
        self.is_even = bool(int(is_even))
        self.day = int(day)
        self.time_ = time_
        self.notify_lag_min = notify_lag_min
        self.is_notified = bool(int(is_notified))

    @staticmethod
    def row_factory():
        return lambda cursor, row: MeetingWeeklyDouble(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]
        )

    def get_notify_text(self):
        return (f'Напоминание о встрече 👀\n'
                f'Время: {self.time_}\n'
                f'Место: {self.place}\n'
                f'Описание: {self.description}\n\n'
                f'Directed by @{self.username}')

    @staticmethod
    def define_week_period_string(period):
        return {
            1: 'начиная с текущей',
            2: 'начиная со следующей'
        }[period]

    @staticmethod
    def define_day_string(is_even, day):
        if is_even:
            even_string = 'четным'
        else:
            even_string = 'нечетным'
        return {
            1: f'По {even_string} понедельникам',
            2: f'По {even_string} вторникам',
            3: f'По {even_string} средам',
            4: f'По {even_string} четвергам',
            5: f'По {even_string} пятницам'
        }[day]

    def get_day_string(self):
        return MeetingWeeklyDouble.define_day_string(self.is_even, self.day)

    @staticmethod
    def get_added_text(is_even, kwargs):
        return (f'Добавлена встреча 🐣\n'
                f'Раз в две недели ({MeetingWeeklyDouble.define_week_period_string(int(kwargs["period"]))})\n'
                f'{MeetingWeeklyDouble.define_day_string(is_even, int(kwargs["day"]))}, в {kwargs["time"]}\n'
                f'Место: {kwargs["place"]}\n'
                f'Описание: {kwargs["description"]}\n'
                f'Лаг оповещения в минутах: {kwargs["notify_lag_min"]}\n\n'
                f'Directed by @{kwargs["username"]}')

    def get_view_with_chat_title(self):
        return f'{self.chat_title}. {self.get_day_string()}, в {self.time_}'

    def get_view_short(self):
        return f'{self.get_day_string()}, в {self.time_}'
