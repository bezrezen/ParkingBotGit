from cgitb import text
import telebot as TB
import sqlite3
from telebot import *
import botconfig

bot = TB.TeleBot(botconfig.token)

db=sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
  user INTEGER UNIQUE ,
  p_number TEXT,
  c_number TEXT);
  """)
db.commit()


@bot.message_handler(commands=['start'])
def starting_message(message):
  kboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  new_user = types.KeyboardButton('Я новый пользователь')
  menya_zaperli = types.KeyboardButton('Проезду мешает чужой автомобиль')
  kboard.add(new_user,menya_zaperli, row_width= 1)
  bot.send_message(message.chat.id,"Добрый день. Выберете одну из опций",reply_markup = kboard)


@bot.message_handler(content_types='text')
def registration(message):
    if message.text == 'Я новый пользователь':
      try:
        msg = bot.send_message(message.chat.id, "Вам необходимо зарегистрироваться. Введите ваш контактный номер телефона")
        db=sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (user) VALUES (?)', (message.from_user.id,))
        db.commit()
        bot.register_next_step_handler(msg, phone_reg)
      except:
        bot.send_message(message.chat.id, "Такой пользователь уже есть")
    elif message.text == 'Проезду мешает чужой автомобиль':
        msg_2 = bot.send_message(message.chat.id, "Введите номер мешающего автомобиля в формате А111АА11")
        bot.register_next_step_handler(msg_2, meshaet)

def meshaet(message):
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    search_res = cursor.execute(f'SELECT p_number FROM users WHERE c_number == ?', (message.text,)).fetchone() 
    bot.send_message(message.chat.id, f"Владелец авто,которое вам мешает: {search_res}")
    print(search_res)

def phone_reg(message):
    msg = bot.send_message (message.chat.id, f"Ваш телефон: {message.text}")
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute(f'UPDATE users SET p_number = (?) WHERE user = {message.from_user.id}', (message.text,))
    db.commit()
    bot.send_message (message.chat.id, "Теперь введите номер автомобиля")
    bot.register_next_step_handler(msg, car_number_reg)

def car_number_reg(message):
    msg = bot.send_message (message.chat.id, f"Ваш номер автомобиля: {message.text}")
    db=sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute(f'UPDATE users SET c_number = (?) WHERE user = {message.from_user.id}', (message.text,))
    db.commit()
    bot.send_message (message.chat.id, "Отлично! Регистрация завершена!")



bot.infinity_polling()
