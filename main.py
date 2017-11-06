import logging
import telegram
import getpass
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, Filters
from schedule import handle_schedule, inline_callback_button, add_task

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

print('Hi, wanna give me some credentials? \n')
bot_token = input('Your bot`s Token: ')
db_username = input('Username: ')
db_password = getpass.getpass('Password: ')

try:
	updater = Updater(token=bot_token)
	dispatcher = updater.dispatcher
except:
    print("Ooops, some unexpected error here: ", sys.exc_info()[0])
    raise

def start(bot, update):
	reply_markup = telegram.ReplyKeyboardRemove()
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, how can I help you?", reply_markup=reply_markup)

def echo(bot, update):
	if hasattr(update.message, 'reply_to_message'):
		orig_mes = update.message.reply_to_message.text
		if 'Which task to add on' in orig_mes:
			add_task(orig_mes[len(orig_mes)-4:len(orig_mes)-1], update.message.text)
	else:
		bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that. :c")

start_handler = CommandHandler('start', start)
sc_handler = CommandHandler('sc', handle_schedule)
echo_handler = MessageHandler(Filters.text, echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(sc_handler)
dispatcher.add_handler(CallbackQueryHandler(inline_callback_button))
dispatcher.add_handler(echo_handler)

updater.start_polling()

updater.idle()