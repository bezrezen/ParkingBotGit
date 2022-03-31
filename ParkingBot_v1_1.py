from cgitb import text
from datetime import datetime
import telebot as TB
import sqlite3
from telebot import types
import botconfig
import datetime
import time

bot = TB.TeleBot(botconfig.token)

db=sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
  user INTEGER UNIQUE ,
  p_number TEXT,
  c_number TEXT,
  status TEXT);
  """)
db.commit()

#сообщение с командами
@bot.message_handler(commands=['start'])
def starting_message(message):
  bot.send_message(message.chat.id,f"Добрый день. Выберете одну из опций \n /registration \n /help \n /functions")

#запись данных пользователя в БД
@bot.message_handler(commands=['registration'])
def registration(message):
  try:
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (user) VALUES (?)', (message.from_user.id,))
    db.commit()
    msg = bot.send_message(message.chat.id, "Введите ваш контактный номер телефона")
    bot.register_next_step_handler(msg, phone_reg)
  except:
    registration_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    reg_succ = types.KeyboardButton('Регистрация корректная')
    reg_unsucc = types.KeyboardButton('Ошибся при регистрации')
    registration_keyboard.add(reg_succ,reg_unsucc, row_width= 2)
    msg_2 = bot.send_message(message.chat.id, "Такой пользователь уже есть. Регистрация прощла правильно?", reply_markup = registration_keyboard)
    bot.register_next_step_handler(msg_2, delete_user)

#пользователь может описать ошибку и она улетает в лог
@bot.message_handler(commands=['help'])
def help(message):
  msg = bot.send_message(message.chat.id, 'Если у вас возникла какая-либо проблема с использованием бота, опишите ее и отправьте.')
  bot.register_next_step_handler(msg, error_log)


@bot.message_handler(commands=['functions'])
def main_func(message):
  func_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  menya_zaperli = types.KeyboardButton('Проезду мешает чужой автомобиль')
  uehal = types.KeyboardButton('Я уехал')
  priehal = types.KeyboardButton('Я приехал')
  func_keyboard.add(uehal,priehal,menya_zaperli, row_width= 2)
  bot.send_message(message.chat.id,"Выберете одну из опций",reply_markup = func_keyboard)


@bot.message_handler(content_types='text')
def user_func(message):
  if message.text == 'Проезду мешает чужой автомобиль':
    msg_2 = bot.send_message(message.chat.id, "Введите номер мешающего автомобиля в формате А111АА11")
    bot.register_next_step_handler(msg_2, meshaet)
  elif message.text == 'Я приехал':
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute(f'UPDATE users SET status = (?) WHERE user = {message.from_user.id}', ('1',))
    db.commit()
    bot.send_message (message.chat.id, "Добро пожаловать!")
  elif message.text == 'Я уехал':
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute(f'UPDATE users SET status = (?) WHERE user = {message.from_user.id}', ('0',))
    db.commit()
    bot.send_message (message.chat.id, "Удачной дороги!")
  else:
    bot.send_message (message.chat.id, f'Простите, я вас не понял. \nПопробуйте выбрать другой вариант')



#удаление пользователя из БД в случае неудачной регистрации
def delete_user(message):
  if message.text == 'Ошибся при регистрации':
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM users WHERE user = (?)', (message.from_user.id,))
    db.commit()
    bot.send_message(message.chat.id, f'Удаление прошло успешно. \nТеперь можно зарегистрироваться повторно. \n\nНажмите /registration')
  elif message.text == 'Регистрация корректная':
    bot.send_message (message.chat.id, 'Отлично. Можем продолжать')

#поиск в БД номера авто и вывод соостветствующего ему номера телефона
def meshaet(message):
  search_data = str(message.text)
  db=sqlite3.connect("database.db")
  cursor = db.cursor()
  search_res = cursor.execute(f'SELECT p_number FROM users WHERE c_number == ?', (search_data,)).fetchone()
  if search_res is None:
    bot.send_message(message.chat.id, 'Такого автомобиля не зарегистрировано, либо вы ошиблись')
  else:
    search_res = ''.join(search_res)
    bot.send_message(message.chat.id, f"Владелец авто,которое вам мешает: {search_res}")

#добавление мобильного телефона пользователя в БД
def phone_reg(message):
  msg = bot.send_message (message.chat.id, f"Ваш телефон: {message.text}")
  db=sqlite3.connect("database.db")
  cursor = db.cursor()
  cursor.execute(f'UPDATE users SET p_number = (?) WHERE user = {message.from_user.id}', (message.text,))
  db.commit()
  bot.send_message (message.chat.id, "Теперь введите номер автомобиля")
  bot.register_next_step_handler(msg, car_number_reg)

#добавление номера автомобиля пользователя в БД
def car_number_reg(message):
  msg = bot.send_message (message.chat.id, f"Ваш номер автомобиля: {message.text}")
  db=sqlite3.connect("database.db")
  cursor = db.cursor()
  cursor.execute(f'UPDATE users SET c_number = (?) WHERE user = {message.from_user.id}', (message.text,))
  db.commit()
  bot.send_message(message.chat.id, "Отлично! Регистрация завершена!")

#добавление сообщения пользователя в лог ошибок
def error_log(message):
  with open(u'bot_error_log.txt','a') as f:
    f.write (str(message.from_user.id)+'\n'+message.text+'\n')
    f.close()
  bot.send_message(message.chat.id, 'Спасибо за отзыв')


bot.infinity_polling()