import MySQLdb
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

def handle_schedule(bot, update):
	keyboard = [[InlineKeyboardButton("<< Main", callback_data='main_menu'), InlineKeyboardButton("Add Task", callback_data='add_task_ask_day')],[InlineKeyboardButton("Check Schedule", callback_data='check_cur')]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="What would you like to do?", reply_markup=reply_markup)

def inline_callback_button(bot, update):
	query = update.callback_query
	if 'add_task' in query.data:
		handle_add_task(bot, query)
	else:
		bot.edit_message_text(text="Selected option: {}".format(query.data), chat_id=query.message.chat_id, message_id=query.message.message_id)
	
def handle_add_task(bot, query):
	if (query.data == 'add_task_ask_day'):
		keyboard = [
			[InlineKeyboardButton("Mon", callback_data='add_task_mon')],
			[InlineKeyboardButton("Tue", callback_data='add_task_tue')],
			[InlineKeyboardButton("Wed", callback_data='add_task_wed')],
			[InlineKeyboardButton("Thu", callback_data='add_task_thu')],
			[InlineKeyboardButton("Fri", callback_data='add_task_fri')],
			[InlineKeyboardButton("Sat", callback_data='add_task_sat')],
			[InlineKeyboardButton("Sun", callback_data='add_task_sun')]
		]
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="Choose day: "
		)

		reply_markup = InlineKeyboardMarkup(keyboard)

		bot.edit_message_reply_markup(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			reply_markup=reply_markup
		)
	else:
		reply_markup = ForceReply(force_reply=True)
		bot.send_message(chat_id=query.message.chat_id, text="Which task to add on {}?".format(query.data[len(query.data)-3:]), reply_markup=reply_markup)


def add_task(day, task):
	
