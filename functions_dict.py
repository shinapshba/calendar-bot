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
            }
        }

    def get_commands_production(self):
        return {
            6: {
                'name': 'Неделя',
                'function': self.production.week
            },
            7: {
                'name': 'Месяц',
                'function': self.production.month
            },
            8: {
                'name': 'Квартал',
                'function': self.production.quarter
            },
            9: {
                'name': 'Год',
                'function': self.production.year
            }
        }
