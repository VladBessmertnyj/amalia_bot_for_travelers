from loader import bot


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                               'text', 'location', 'contact', 'sticker'])
def default_command(message):
    bot.send_message(message.chat.id, 'Извините, я Вас не поняла.')
