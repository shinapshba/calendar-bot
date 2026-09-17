class FunctionsDict:
    def __init__(self, bot, admin, meeting):
        self.bot = bot
        self.admin = admin
        self.meeting = meeting

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
                'name': 'Удалить оповещения',
                'function': self.admin.delete_notifies
            }
        }
