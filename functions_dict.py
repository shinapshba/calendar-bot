class FunctionsDict:
    def __init__(self, bot, admin, meeting, production):
        self.bot = bot
        self.admin = admin
        self.meeting = meeting
        self.production = production

    def get_commands_meeting(self):
        return {
            1: {
                'name': 'Добавить встречу',
                'function': self.meeting.add
            },
            2: {
                'name': 'Удалить встречу',
                'function': self.meeting.delete
            },
            3: {
                'name': 'Показать встречи',
                'function': self.meeting.show
            }
        }

    def get_commands_admin(self):
        return {
            4: {
                'name': 'Просмотр пользователей',
                'function': self.admin.show_users
            },
            5: {
                'name': 'Файл логов',
                'function': self.admin.logs
            },
            6: {
                'name': 'Просмотр выходных',
                'function': self.admin.show_day_off
            },
            7: {
                'name': 'Добавить выходной',
                'function': self.admin.add_day_off
            },
            8: {
                'name': 'Удалить выходные',
                'function': self.admin.delete_day_off
            }
        }

    def get_commands_production(self):
        return {
            9: {
                'name': 'Неделя',
                'function': self.production.week
            },
            10: {
                'name': 'Месяц',
                'function': self.production.month
            },
            11: {
                'name': 'Квартал',
                'function': self.production.quarter
            },
            12: {
                'name': 'Год',
                'function': self.production.year
            }
        }
