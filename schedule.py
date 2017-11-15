import MySQLdb
import sys
import telegram
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyKeyboardMarkup

def handle_schedule(bot, update, chat_data):
	keyboard = [[InlineKeyboardButton("<< Main", callback_data='main_menu')],
				[InlineKeyboardButton("Remove Section", callback_data='del_sec_ask_sec'), InlineKeyboardButton("Add Section", callback_data='add_sec')],
				[InlineKeyboardButton("Remove Task", callback_data='del_task_ask_day'), InlineKeyboardButton("Add Task", callback_data='add_task_ask_section')],
				[InlineKeyboardButton("Check Schedule", callback_data='check_cur_ask_day')]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="What would you like to do?", reply_markup=reply_markup)

def inline_callback_button(bot, update, chat_data):
	query = update.callback_query
	if 'add_task' in query.data:
		handle_add_task(bot, query, chat_data)
	elif 'check_cur' in query.data:
		handle_check_schedule(bot, query, chat_data)
	elif 'del_task' in query.data:
		handle_del_task(bot, query, chat_data)
	elif 'add_sec' in query.data:
		handle_add_section(bot, query, chat_data)
	elif 'del_sec' in query.data:
		handle_del_section(bot, query, chat_data)
	else:
		bot.answer_callback_query(query.id)
		custom_keyboard = [['/start', '/sc']]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		bot.send_message(text="I'm a bot, how can I help you?".format(query.data), chat_id=query.message.chat_id, reply_markup=reply_markup)

def handle_add_section(bot, query, chat_data):
	reply_markup = ForceReply(force_reply=True)
	bot.send_message(chat_id=query.message.chat_id, text="Input your section`s name", reply_markup=reply_markup)

def handle_del_section(bot, query, chat_data):
	if 'del_sec_ask_sec' in query.data:
		display_section_to_choose_callback(bot, query, chat_data,'del_sec_')
	else:
		delete_section(query.data[8:], chat_data, bot, query)

def display_week_to_choose_callback(bot, query, _callback_data):
	keyboard = [
			[InlineKeyboardButton("Mon", callback_data=_callback_data+'_day_mon')],
			[InlineKeyboardButton("Tue", callback_data=_callback_data+'_day_tue')],
			[InlineKeyboardButton("Wed", callback_data=_callback_data+'_day_wed')],
			[InlineKeyboardButton("Thu", callback_data=_callback_data+'_day_thu')],
			[InlineKeyboardButton("Fri", callback_data=_callback_data+'_day_fri')],
			[InlineKeyboardButton("Sat", callback_data=_callback_data+'_day_sat')],
			[InlineKeyboardButton("Sun", callback_data=_callback_data+'_day_sun')]
		]
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="Choose day: ")
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.edit_message_reply_markup(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		reply_markup=reply_markup)

def display_section_to_choose_callback(bot, query, chat_data, _callback_data):
	sections = get_categories(query.message.chat_id, chat_data['db_username'], chat_data['db_password'])
	if len(sections) > 0:
		keyboard = []
		for section in sections:
			keyboard.append([InlineKeyboardButton("{}".format(section[1]), callback_data=_callback_data+"{}".format(section[0]))])
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="Choose section: ")
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.edit_message_reply_markup(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			reply_markup=reply_markup)
	else:
		bot.send_message(chat_id=query.message.chat_id, text="Sorry, you don`t have any sections enrolled yet.")


def handle_del_task(bot, query, chat_data):
	if (query.data == 'del_task_ask_day'):
		display_week_to_choose_callback(bot, query, 'del_task')
	else:
		if ('del_task_selected' in query.data):
			delete_task(query.data[18:], chat_data, bot, query)
		else:
			build_remove_markup_tasks_day(bot, query, chat_data)

def build_remove_markup_tasks_day(bot, query, chat_data):
	short_week_day = query.data[len(query.data)-3:]
	activities = get_tasks_day(short_week_day, query.message.chat_id, chat_data['db_username'], chat_data['db_password'])
	keyboard = []
	for activity in activities:
		activity_name = activity[9]
		activity_id = activity[7]
		keyboard.append([InlineKeyboardButton("{}".format(activity_name), callback_data="del_task_selected_{}".format(activity_id))])
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="Choose a task to remove: ")
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.edit_message_reply_markup(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			reply_markup=reply_markup)

def handle_add_task(bot, query, chat_data):
	if ('add_task_sec_' in query.data and '_day' in query.data):
		reply_markup = ForceReply(force_reply=True)
		chat_data['add_task_day'] = query.data[len(query.data)-3:]
		chat_data['add_task_section'] = query.data[13:len(query.data)-8]
		bot.send_message(chat_id=query.message.chat_id, text="Which task to add?", 
						reply_markup=reply_markup)
		bot.answer_callback_query(query.id)
	elif (query.data == 'add_task_ask_section'):
		display_section_to_choose_callback(bot, query, chat_data,'add_task_sec_')
	else:
		display_week_to_choose_callback(bot, query, query.data)

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
			text="Check for: ")
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.edit_message_reply_markup(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			reply_markup=reply_markup)
	else:
		days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
		if 'week' in query.data:
			for day in days:
				custom_keyboard = [['/start', '/sc']]
				reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
				bot.send_message(chat_id=query.message.chat_id, text=show_task_day(day, query.message.chat_id, chat_data['db_username'], chat_data['db_password']), parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
				bot.answer_callback_query(query.id)
		else:
			weekno = datetime.datetime.today().weekday()
			custom_keyboard = [['/start', '/sc']]
			reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
			bot.send_message(chat_id=query.message.chat_id, text=show_task_day(days[weekno], query.message.chat_id, chat_data['db_username'], chat_data['db_password']), parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
			bot.answer_callback_query(query.id)


def add_task(bot, day, section_id, task, db_user, db_passwd, user_id):
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
				cur.execute("INSERT INTO activity (weekday_id, name, status, section_id) VALUES ({}, \'{}\', NULL, {})".format(weekday[0], task, section_id))
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
	short_names = {
		'mon': 'Monday',
		'tue': 'Tuesday',
		'wed': 'Wednesday',
		'thu': 'Thursday',
		'fri': 'Friday',
		'sat': 'Saturday',
		'sun': 'Sunday'
	}
	activities = get_tasks_day(day, user_id, db_username, db_password)
	sections = []
	message = "_{}_".format(short_names[day])

	for activity in activities:
		if activity[13] not in sections:
			sections.append(activity[13])
	
	for section in sections:
		formatted_section = format_section(section)
		message = message + " \n "
		message = message + " \n "
		message = message + "`{}`".format(formatted_section)
		message = message + " \n "
		section_activities = list(filter((lambda act: act[13] == section), activities))
		for section_activity in section_activities:
			message = message + "{}".format(section_activity[9])
			message = message + " \n "
	return message

def format_section(section):
	result = ""
	for letter in section:
		result = result + letter.upper() + " "
	return result

def get_tasks_day(day, user_id, db_username, db_password):
	db = MySQLdb.connect(host="localhost", user=db_username, passwd=db_password, db="schedule")
	cur = db.cursor()
	cur.execute("SELECT * FROM users \
					INNER JOIN weekday ON weekday.user_id = users.id \
					INNER JOIN activity ON activity.weekday_id = weekday.id \
					INNER JOIN section ON section.id = activity.section_id \
					WHERE users.id = {} AND short_name = \'{}\'".format(user_id, day))
	activities = tuple(cur.fetchall())
	db.close()
	return activities

def get_categories(user_id, db_username, db_password):
	db = MySQLdb.connect(host="localhost", user=db_username, passwd=db_password, db="schedule")
	cur = db.cursor()
	cur.execute("SELECT * FROM section WHERE user_id = {}".format(user_id))
	sections = tuple(cur.fetchall())
	db.close()
	return sections
	
def delete_task(task_id, chat_data, bot, query):
	db = MySQLdb.connect(host="localhost", user=chat_data['db_username'], passwd=chat_data['db_password'], db="schedule")
	cur = db.cursor()
	cur.execute("DELETE FROM activity WHERE id = {}".format(task_id))
	db.commit()
	db.close()
	custom_keyboard = [['/start', '/sc']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=query.message.chat_id, text="The task was successfully deleted", reply_markup=reply_markup)
	bot.answer_callback_query(query.id)
	return

def add_section(bot, section_text, db_username, db_password, user_id):
	db = MySQLdb.connect(host="localhost", user=db_username, passwd=db_password, db="schedule")
	cur = db.cursor()
	cur.execute("INSERT INTO section (user_id, name) VALUES ({}, \'{}\')".format(user_id, section_text))
	db.commit()
	db.close()
	custom_keyboard = [['/start', '/sc']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=user_id, text="*{}* section was successfully added.".format(section_text), 
						parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)


def delete_section(section_id, chat_data, bot, query):
	db = MySQLdb.connect(host="localhost", user=chat_data['db_username'], passwd=chat_data['db_password'], db="schedule")
	cur = db.cursor()
	cur.execute("DELETE FROM activity WHERE section_id = {}".format(section_id))
	db.commit()
	cur.execute("DELETE FROM section WHERE id = {}".format(section_id))
	db.commit()
	db.close()
	custom_keyboard = [['/start', '/sc']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=query.message.chat_id, text="The section was successfully deleted", reply_markup=reply_markup)
	bot.answer_callback_query(query.id)
	return