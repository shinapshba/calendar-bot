import datetime


def is_today_is_day_of_month(day_of_month: int):
    return datetime.datetime.now().day == day_of_month


def is_date_tomorrow(date_time_string: str):
    date = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M').date()
    tomorrow_date = date.today() + datetime.timedelta(days=1)
    return date == tomorrow_date


def is_date_today(date_time_string: str):
    today_date_string = datetime.date.today().strftime('%Y-%m-%d')
    return today_date_string == date_time_string.split(' ')[0]


def is_datetime_delta_passed_minutes(date_time_string: str, minutes: int):
    date_time = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M')
    date_time_now = datetime.datetime.now()
    if date_time_now > date_time:
        return False
    delta_minutes = (date_time - date_time_now).total_seconds() / 60
    return delta_minutes <= minutes


def is_time_delta_passed_minutes(time_string: str, minutes: int):
    date_time_string = datetime.date.today().strftime('%Y-%m-%d') + ' ' + time_string
    date_time = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M')
    date_time_now = datetime.datetime.now()
    if date_time_now > date_time:
        return False
    delta_minutes = (date_time - date_time_now).total_seconds() / 60
    return delta_minutes <= minutes


def is_in_future(date_time_string):
    date_time = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M')
    return date_time > datetime.datetime.now()


def is_in_future_time(time_string):
    date_time_string = datetime.date.today().strftime('%Y-%m-%d') + ' ' + time_string
    date_time = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M')
    return date_time > datetime.datetime.now()


def is_current_week_even():
    return datetime.datetime.now().isocalendar()[1] % 2 == 0


def is_current_day_working():
    return datetime.datetime.now().isoweekday() not in [6, 7]


def get_current_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_current_date():
    return datetime.date.today().strftime("%Y-%m-%d")
