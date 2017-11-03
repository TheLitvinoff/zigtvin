import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

updater = Updater(token="479323920:AAHzN1pOgSvUlCSfdNr8ALBXUT0gMHLI6pM")
dispatcher = updater.dispatcher


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
	reply_markup = telegram.ReplyKeyboardRemove()
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!", reply_markup=reply_markup)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)



def echo(bot, update):
	if "саша" in str.lower(update.message.text):
		bot.send_message(chat_id=update.message.chat_id, text="Так все мы знаем, что Саша - козявка.")
	elif "слава" in str.lower(update.message.text):
		bot.send_message(chat_id=update.message.chat_id, text="Ну а Слава - молодец.")
	else:
		bot.send_message(chat_id=update.message.chat_id, text="Даже не знаю, что ответить. :(")

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)


def whois(bot, update, args):
	reply = "Даже не знаю, что ответить. :("
	if "саша" in str.lower(args):
		reply = "Так все мы знаем, что Саша - козявка."
	elif "слава" in str.lower(args):
		reply = "Ну а Слава - молодец."

	bot.send_message(chat_id=update.message.chat_id, text=reply)

whois_handler = CommandHandler('whois', whois, pass_args=True)
dispatcher.add_handler(whois_handler)


updater.start_polling()