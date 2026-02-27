import model
import telebot


class BotExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        print(f'Error in bot: {exception}')
        return True


bot = telebot.TeleBot(model.select_token(), exception_handler=BotExceptionHandler())

bot.set_my_commands([
    telebot.types.BotCommand('/start', 'Начало работы'),
    telebot.types.BotCommand('/meeting', 'Управление встречами'),
    telebot.types.BotCommand('/health_check', 'Проверка работоспособности')
])
