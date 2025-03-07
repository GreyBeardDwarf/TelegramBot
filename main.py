import sys

import telebot
from telebot import types
import config
from config import token
import wikipedia
import re
import sqlite3
from sys import *
import random
conn = sqlite3.connect("users.db",check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users(id INT);")
conn.commit()
statis = ["Германия","Римская империя","Хомяк","Евреи"]
bot = telebot.TeleBot(token)
wiki_on = False
admins = [1501054584]
text = ""
link = ""
clients = []
@bot.message_handler(commands=["wikipedia"])
def wiki_funk(message):
    wiki_markup = types.InlineKeyboardMarkup()
    bot_ser = types.InlineKeyboardButton(text="Yeap, i want that",callback_data="Yeap, i want that")
    bot_not_ser = types.InlineKeyboardButton(text="Not this",callback_data="Not this")
    wiki_markup.add(bot_not_ser,bot_ser)
    bot.send_message(message.chat.id,"are you want to find smt?",reply_markup=wiki_markup)


@bot.message_handler(commands=["start"])
def test(message):
    if message.chat.id in admins:
        help(message)
    else:
        info = cur.execute("SELECT * FROM users WHERE id=?", (message.chat.id,)).fetchone()
        if not info:
            cur.execute("INSERT INTO users (id) VALUES (?)",(message.chat.id,))
            conn.commit()
            bot.send_message(message.chat.id,"now you will get links")
    # keyboard = types.InlineKeyboardMarkup()
    # button_y = types.InlineKeyboardButton(text="yes", callback_data="yes")
    # button_n = types.InlineKeyboardButton(text="no", callback_data="no")
    # keyboard.add(button_y,button_n)
    # bot.send_message(message.chat.id,"what are you want?",reply_markup=keyboard)
def help(message):
    replay_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
    replay_board.add(types.KeyboardButton(text="Text for sending"))
    replay_board.add(types.KeyboardButton(text="create link"))
    replay_board.add(types.KeyboardButton(text="show mes for sending"))
    replay_board.add(types.KeyboardButton(text="starting"))
    replay_board.add(types.KeyboardButton(text="help"))
    bot.send_message(message.chat.id, "bot's Commands: \n"
                                      "/create_text\n"
                                      "/create_link\n"
                                      "/show_message\n"
                                      "/start_linking\n"
                                      "/help", reply_markup=replay_board)
@bot.message_handler(commands=["create_text"])
def create_text(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id,'enter the text')
        bot.register_next_step_handler(m,new_text)

def new_text(message):
    global text
    text = message.text
    if text not in ['тапайте бурундучков']:
        bot.send_message(message.chat.id,f'saved text: {text}')
    else:
        bot.send_message(message.chat.id,"error😡")

@bot.message_handler(commands=["create_link"])
def edit_link(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, 'enter the link')
        bot.register_next_step_handler(m, add_link)

def add_link(message):
    global link
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # проверка dot
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # проверка ip 
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if message.text is not None and regex.search(message.text):
        link = message.text
        bot.send_message(message.chat.id, f'saved the link: {link}')
    else:
        m = bot.send_message(message.chat.id, 'enter is incorrect')
        bot.register_next_step_handler(m, add_link)
@bot.message_handler(commands=["show_message"])
def show_mes(message):
    global text, link
    if message.chat.id in admins:
        if text != "":
            if link != "":
                bot.send_message(message.chat.id,text,f"{text}{link}")


@bot.message_handler(commands=["start_linking"])
def start_linking(message):
    global link, text
    if message.chat.id in admins:
        if text != "":
            if link != "":
                cur.execute("SELECT id FROM users")
                massive = cur.fetchall()
                for client_id in massive:
                    id = client_id[0]
                    sending(id)
                else:
                    text = ""
                    link = ""
            else:
                bot.send_message(message.chat.id,"the link is empty")
        else:
            bot.send_message(message.chat.id, "the text is empty")
def sending(id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="The link on web", url=link))
    bot.send_message(id,text,reply_markup=markup)
@bot.message_handler(commands=["hello"])
def test(message):
    bot.send_message(message.chat.id,"has sent the message")


@bot.message_handler(content_types=["text"])
def get_text(message):
    if wiki_on is True:
        text = message.text
        wiki_text = create_wiki(text)
        bot.send_message(message.chat.id,wiki_text)
    if "hello" == message.text:
        bot.send_message(message.chat.id, "you goofy ahh bro")
    if "id" == message.text:
        bot.send_message(message.chat.id,f"id:{message.from_user}")
    elif "Text for sending" == message.text:
        create_text(message)
    elif "create link" == message.text:
        edit_link(message)
    elif "Randy" == message.text:
        ran_wiki(message)

@bot.callback_query_handler(func=lambda call:True)
def button(call):
    global wiki_on
    if call.data == "yes":
        bot.send_message(call.message.chat.id,"🤫")
        replay_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_rep = types.KeyboardButton(text="id")
        replay_board.add(button_rep)
        bot.send_message(call.message.chat.id, "what are you want?🤓",reply_markup=replay_board)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "😡😈")
    if call.data == "Yeap, i want that":
        wiki_on = True
        bot.send_message(call.message.chat.id,"Catch this")
    if call.data == "Not this":
        wiki_on = False
        bot.send_message(call.message.chat.id, "alright")
wikipedia.set_lang("ru")

def ran_wiki(message):
    word = random.choice(statis)
    bot.send_message(message.chat.id,create_wiki(word))

def create_wiki(word):
    try:
        wiki = wikipedia.page(word)
        wiki_text = wiki.content[:1000]
        wiki_result = wiki_text.split(".")
        wiki_result = wiki_result[:-1]
        wiki_result_2 = ""
        for i in wiki_result:
            if not("==" in i):
                wiki_result_2 = wiki_result_2 + i + "."
        wiki_result_2 = re.sub("\([^()]*\)","",wiki_result_2)
        return wiki_result_2
    except:
        return "has not found wikipedia"

bot.infinity_polling()
print("Lesson_2")
print("HEllO")
#нопомнить что такое вот эти вот приколы: __def(or smt difer)__