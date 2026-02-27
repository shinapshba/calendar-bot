import model

class Admin:
    def __init__(self, bot):
        self.bot = bot

    def show_users(self, call):
        chats = model.select_all_chats()
        text = '\n'.join(sorted(list(map(lambda c: c.to_string(), chats))))
        self.bot.send_message(call.message.chat.id, text)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)