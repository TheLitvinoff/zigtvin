import logging
import telegram
import getpass
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, Filters
from telegram import ReplyKeyboardMarkup
import schedule

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
print("     ********************************************************")
print("     |                                                      |")
print('     |              Telegram Zigtvin Bot                    |')
print("     |                                                      |")
print("     ********************************************************\n")

t = input('Bot`s Token: ')
u = input('DB username: ')
p = getpass.getpass('DB password: ')

bot_token = str(t)
db_username = str(u)
db_password = str(p)

try:
	updater = Updater(token=bot_token)
	dispatcher = updater.dispatcher
except:
    print("Ooops, some unexpected error here: ", sys.exc_info()[0])
    raise

def start(bot, update):
	custom_keyboard = [['/start', '/sc']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, how can I help you?", reply_markup=reply_markup)

def sc(bot, update, chat_data):
	chat_data['db_username'] = db_username
	chat_data['db_password'] = db_password
	schedule.handle_schedule(bot, update, chat_data)

def echo(bot, update, chat_data):
	if hasattr(update.message, 'reply_to_message'):
		orig_mes = update.message.reply_to_message.text
		if 'Which task to add' in orig_mes:
			schedule.add_task(bot, chat_data['add_task_day'], chat_data['add_task_section'],update.message.text, db_username, db_password, update.message.chat_id)
		elif 'Input your section`s name' in orig_mes:
			schedule.add_section(bot, update.message.text, db_username, db_password, update.message.chat_id)
		else:
			bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that. :c")
	else:
		bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that. :c")

start_handler = CommandHandler('start', start)
sc_handler = CommandHandler('sc', sc, pass_chat_data=True)
echo_handler = MessageHandler(Filters.text, echo, pass_chat_data=True)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(sc_handler)
dispatcher.add_handler(CallbackQueryHandler(schedule.inline_callback_button, pass_chat_data=True))
dispatcher.add_handler(echo_handler)

updater.start_polling()

updater.idle()