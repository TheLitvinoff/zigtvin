import logging
import telegram
from telegram.ext import Updater, CommandHandler 

updater = Updater(token="479323920:AAHzN1pOgSvUlCSfdNr8ALBXUT0gMHLI6pM")
dispatcher = updater.dispatcher


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
	reply_markup = telegram.ReplyKeyboardRemove()
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!", reply_markup=reply_markup)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)



updater.start_polling()