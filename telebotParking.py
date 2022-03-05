from cgitb import text
import telebot as TB
import sqlite3
from telebot import *
import botconfig

bot = TB.TeleBot(botconfig.token)

db=sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
  user TEXT UNIQUE PRIMARY KEY,
  p_number TEXT,
  c_number TEXT);
  """)
db.commit()

@bot.message_handler(commands=['start'])
def start_message(message):
  kboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  new_user = types.KeyboardButton('Я новый пользователь')
  menya_zaperli = types.KeyboardButton('Проезду мешает чужой автомобиль')
  kboard.add(new_user,menya_zaperli, row_width= 1)
  bot.send_message(message.chat.id,"Добрый день. Выберете одну из опций",reply_markup = kboard)
  

@bot.message_handler(content_types=['text'])
def new(message):
  if message.text == 'Я новый пользователь':
    bot.send_message(message.chat.id, "Вам необходимо зарегистрироваться")
    bot.send_message(message.chat.id, "Введите номер Вашего автомобиля и Ваш контактный телефон в формате +7(***)***-**-** , А 111 АА 11")

@bot.message_handler(content_types=['text'])
def registration(message):
  db=sqlite3.connect("database.db")
  cursor = db.cursor()
  cursor.execute('INSERT INTO users (user, p_number, c_number) VALUES (?,?,?)', (message.user.id, 1, 2))
  db.commit()

#@bot.message_handler(content_types=['text'])
#def zaperli(message):
  #if message.text == 'Проезду мешает чужой автомобиль':
    #db[message.from_user.id]

bot.infinity_polling()