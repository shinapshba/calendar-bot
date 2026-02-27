class Chat:
    def __init__(self, chat_id, username, title):
        self.chat_id = chat_id
        self.username = username
        self.title = title

    def to_string(self):
        if self.username is not None:
            return f'Пользователь @{self.username}'
        return f'Чат "{self.title}"'
