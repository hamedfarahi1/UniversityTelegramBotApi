from telegram.ext import Updater, CommandHandler


def bop(bot, update):
    chat_id = update.message.chat_id
    img = open('./captcha_3KrhPAnC1F.png', 'rb')
    bot.send_message(chat_id=chat_id,text="hello")

def main():
    updater = Updater(
        "683517472:AAGv7Actm6Rr1foyapvTyvPnNsIaFKiUxiA")
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
