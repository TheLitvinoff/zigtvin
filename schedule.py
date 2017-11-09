import MySQLdb
import sys
import telegram
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

def handle_schedule(bot, update, chat_data):
	keyboard = [[InlineKeyboardButton("<< Main", callback_data='main_menu'), InlineKeyboardButton("Add Task", callback_data='add_task_ask_day')],[InlineKeyboardButton("Check Schedule", callback_data='check_cur_ask_day')]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="What would you like to do?", reply_markup=reply_markup)

def inline_callback_button(bot, update, chat_data):
	query = update.callback_query
	if 'add_task' in query.data:
		handle_add_task(bot, query, chat_data)
	elif 'check_cur' in query.data:
		handle_check_schedule(bot, query, chat_data)
	else:
		bot.edit_message_text(text="Selected option: {}".format(query.data), chat_id=query.message.chat_id, message_id=query.message.message_id)
	
def handle_add_task(bot, query, chat_data):
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
		bot.answer_callback_query(query.id)

def handle_check_schedule(bot, query, chat_data):
	if (query.data == 'check_cur_ask_day'):
		keyboard = [
			[InlineKeyboardButton("<< Main", callback_data='main_menu'), InlineKeyboardButton("Week", callback_data='check_cur_week')],
			[InlineKeyboardButton("Today", callback_data='check_cur_day')],
		]
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="Check for: "
		)

		reply_markup = InlineKeyboardMarkup(keyboard)

		bot.edit_message_reply_markup(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			reply_markup=reply_markup
		)
	else:
		days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
		if 'week' in query.data:
			for day in days:
				bot.send_message(chat_id=query.message.chat_id, text=show_task(day, query.message.chat_id, chat_data['db_username'], chat_data['db_password']), parse_mode=telegram.ParseMode.MARKDOWN)
				bot.answer_callback_query(query.id)
		else:
			weekno = datetime.datetime.today().weekday()
			bot.send_message(chat_id=query.message.chat_id, text=show_task(days[weekno], query.message.chat_id, chat_data['db_username'], chat_data['db_password']), parse_mode=telegram.ParseMode.MARKDOWN)
			bot.answer_callback_query(query.id)


def add_task(bot, day, task, db_user, db_passwd, user_id):
	short_names = {
		'mon': 'Monday',
		'tue': 'Tuesday',
		'wed': 'Wednesday',
		'thu': 'Thursday',
		'fri': 'Friday',
		'sat': 'Saturday',
		'sun': 'Sunday'
	}
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_passwd, db="schedule")
	cur = db.cursor()

	user = get_or_create_user(db_user, db_passwd, user_id)
	if user:
		weekday = get_or_create_weekday(db_user, db_passwd, user_id, day, short_names[day])
		if weekday:
			try:
				cur.execute("INSERT INTO activity (weekday_id, name, status) VALUES ({}, \'{}\', NULL)".format(weekday[0], task))
				db.commit()
			except:
				db.rollback()
			db.close()
			bot.send_message(chat_id=user_id, text="*{}* was successfully added on *{}*".format(task, short_names[day]), parse_mode=telegram.ParseMode.MARKDOWN)
	return


def get_or_create_user(db_user, db_passwd, user_id):
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_passwd, db="schedule")
	cur = db.cursor()
	cur.execute("SELECT * FROM users WHERE id = {}".format(user_id))
	users = tuple(cur.fetchall())
	if len(users) == 0:
		try:
			cur.execute("INSERT INTO users VALUES ({}, NULL, NULL)".format(user_id))
			db.commit()
		except:
			db.rollback()
		cur.execute("SELECT * FROM users WHERE id = {}".format(user_id))
		users = tuple(cur.fetchall())
	user = users[0] if len(users) > 0 else ()
	db.close()
	return user

def get_or_create_weekday(db_user, db_passwd, user_id, day, short_name):
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_passwd, db="schedule")
	cur = db.cursor()
	cur.execute("SELECT * FROM weekday WHERE user_id = {} AND short_name = \'{}\'".format(user_id, day))
	weekdays = tuple(cur.fetchall())
	if len(weekdays) == 0:
		cur.execute("INSERT INTO weekday (user_id, name, short_name) VALUES (\'{}\', \'{}\', \'{}\')".format(user_id, short_name, day))
		db.commit()
		cur.execute("SELECT * FROM weekday WHERE user_id = {} AND short_name = \'{}\'".format(user_id, day))
		weekdays = tuple(cur.fetchall())
	weekday = weekdays[0] if len(weekdays) > 0 else ()
	db.close()
	return weekday

def show_task_day(day, user_id, db_username, db_password):
	
	if len(activities) > 0:
		activity = activities[0]
		return "{} ------- {}".format(activity[5], activity[9])
	return day


def get_tasksl_day(day, user_id, db_username, db_password):
	db = MySQLdb.connect(host="localhost", user=db_username, passwd=db_password, db="schedule")
	cur = db.cursor()
	cur.execute("SELECT * FROM users INNER JOIN weekday ON weekday.user_id = users.id INNER JOIN activity ON activity.weekday_id = weekday.id WHERE users.id = {} AND short_name = \'{}\'".format(user_id, day))
	activities = tuple(cur.fetchall())
	db.close()
	
