class Day:
    def __init__(self, date: str, weekday: str, work_type: str, work_hours: int, title: str):
        self.date = date
        self.weekday = weekday
        self.work_type = work_type
        self.work_hours = work_hours
        self.title = title

    def to_string(self):
        if self.title is not None:
            title_text = f'. {self.title}'
        else:
            title_text = ''
        return f'{self.date}: {self.weekday}. {self.work_type}, рабочих часов {self.work_hours}' + title_text

    @staticmethod
    def from_dict(data: dict):
        return Day(data['date'], data['weekday']['name'], data['type']['name'], data['working_hours'], data['title'])


class Week:
    def __init__(self, days: list, title: str, work_hours: int, start_date: str, end_date: str):
        self.days = days
        self.title = title
        self.work_hours = work_hours
        self.start_date = start_date
        self.end_date = end_date

    def to_string(self):
        days_text = ';\n'.join(list(map(lambda d: f' - {d.to_string()}', self.days))) + '.'
        return (f'{self.title}\n'
                f'С {self.start_date} по {self.end_date}\n'
                f'Рабочих часов {self.work_hours}\n'
                f'Дни:\n{days_text}')

    @staticmethod
    def from_dict(data: dict):
        days = []
        for day_item in data['days']:
            days.append(Day.from_dict(day_item))
        return Week(days, data['work_week']['name'], data['statistics']['working_hours'],
                    data['dt_start'], data['dt_end'])


class Month:
    def __init__(self, days, work_days: int, weekends: int, holidays: int, work_hours: int,
                 start_date: str, end_date: str):
        self.days = days
        self.work_days = work_days
        self.weekends = weekends
        self.holidays = holidays
        self.work_hours = work_hours
        self.start_date = start_date
        self.end_date = end_date

    def to_string(self):
        days_text = ';\n'.join(list(map(lambda d: f' - {d.to_string()}', self.days))) + '.'
        return (f'Месяц\n'
                f'Период с {self.start_date} по {self.end_date}\n'
                f'Рабочих часов {self.work_hours}\n'
                f'Рабочих дней {self.work_days}\n'
                f'Выходных дней {self.weekends}\n'
                f'Праздничных дней {self.holidays}\nДни:\n' + days_text)

    @staticmethod
    def from_dict(data: dict):
        days = []
        for day_item in data['days']:
            days.append(Day.from_dict(day_item))
        return Month(days, data['statistics']['work_days'], data['statistics']['weekends'],
                     data['statistics']['holidays'], data['statistics']['working_hours'],
                     data['dt_start'], data['dt_end'])


class Quarter:
    def __init__(self, days, work_days: int, weekends: int, holidays: int, work_hours: int,
                 start_date: str, end_date: str):
        self.days = days  # days
        self.work_days = work_days
        self.weekends = weekends
        self.holidays = holidays
        self.work_hours = work_hours
        self.start_date = start_date
        self.end_date = end_date

    def to_string(self):
        days_text = ';\n'.join(list(map(lambda d: f' - {d.to_string()}', self.days))) + '.'
        return (f'Квартал\n'
                f'Период с {self.start_date} по {self.end_date}\n'
                f'Рабочих часов {self.work_hours}\n'
                f'Рабочих дней {self.work_days}\n'
                f'Выходных дней {self.weekends}\n'
                f'Праздничных дней {self.holidays}\nДни:\n' + days_text)

    @staticmethod
    def from_dict(data: dict):
        days = []
        for day_item in data['days']:
            days.append(Day.from_dict(day_item))
        return Month(days, data['statistics']['work_days'], data['statistics']['weekends'],
                     data['statistics']['holidays'], data['statistics']['working_hours'],
                     data['dt_start'], data['dt_end'])
