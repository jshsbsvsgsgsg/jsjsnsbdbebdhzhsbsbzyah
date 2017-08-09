# -*- coding: utf-8 -*-
# Radio Javan bot
# Coded by iTeam
# All rights reserved
import telebot
from telebot import types
import urllib
import sys
import os
import json
import redis
from random import randint
from threading import Thread
import requests
reload(sys)
sys.setdefaultencoding("utf-8")
redis = redis.StrictRedis(host='localhost', port=6379, db=0)
TOKEN = '416134007:AAGqy-10db5LNvwPi3YbuqFE7atImDyUoiM' # توکن ربات
admin = 299157138 # آیدی ادمین
bot = telebot.TeleBot(TOKEN)
bot_user = bot.get_me().username
def getc(attr) :
    hash = 'RJ:contents:' + attr
    if redis.get(hash) :
        return redis.get(hash)
    else :
        if attr == 'link' :
            return "https://google.com"
        else :
            return "متنی برای این بخش تنظیم نشده..."
channel_link = getc('link')
@bot.message_handler(commands=['start'])
def start(m):
    def starts():
        redis.sadd('RJ:users', m.from_user.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('آموزش استفاده از ربات', callback_data='help'))
        markup.add(types.InlineKeyboardButton('ارتباط با سازندگان ربات', callback_data='contact'))
        bot.send_message(m.from_user.id, getc('start'), reply_markup=markup)
    Thread(target=starts).start()
@bot.callback_query_handler(func=lambda call: call.data)
def call(c):
    def calls():
        if c.data == 'help' :
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('برگشت', callback_data='back'))
            bot.edit_message_text(getc('help'), chat_id=c.message.chat.id, message_id=c.message.message_id, reply_markup=markup)
        elif c.data == 'back' :
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('آموزش استفاده از ربات', callback_data='help'))
            markup.add(types.InlineKeyboardButton('ارتباط با سازندگان ربات', callback_data='contact'))
            bot.edit_message_text(getc('start'), chat_id=c.message.chat.id, message_id=c.message.message_id, reply_markup=markup)
        elif c.data == 'contact' :
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('برگشت', callback_data='back'))
            bot.edit_message_text(getc('contact'), chat_id=c.message.chat.id, message_id=c.message.message_id, reply_markup=markup)
    Thread(target=calls).start()
@bot.inline_handler(lambda query: True)
def inline(q):
    def inlines() :
        try :
            params = urllib.urlencode({'query': q.query}).replace('+', '%20')
            data = urllib.urlopen('http://rj.iteam.pw/scsearch.php?'+params).read()
            try :
                data = json.loads(data)
                n = 1
                answers = []
                datas = range(len(data))
                if len(data) > 20 :
                    datas = range(20)
                for i in datas :
                    try :
                        res = data[i]
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('به اشتراک گذاشتن این آهنگ', switch_inline_query=res['permalink']))
                        markup.add(types.InlineKeyboardButton('کانال سازنده ربات', url=channel_link))
                        answers.append(types.InlineQueryResultAudio(str(n), res['download'], res['title']+' (@{})'.format(bot_user), caption=res['title']+'\nBy @{}'.format(bot_user), reply_markup=markup))
                        n = n+1
                    except Exception as e:
                        print(e)
                bot.answer_inline_query(q.id, answers, cache_time=1)
            except :
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('کانال سازنده ربات', url=channel_link))
                ans = types.InlineQueryResultArticle('1', 'ارور ۴۰۴', types.InputTextMessageContent('موزیک مورد نظر یافت نشد!'), reply_markup=markup, description='نتیجه ای یافت نشد', thumb_url='https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRN1XBvOYy2AA5g0cQ4psmiFj7cCnB4Z1M7D5tT_j8506-D0Teh5Q')
                bot.answer_inline_query(q.id, [ans], cache_time=1)
        except Exception as e :
            print(e)
    Thread(target=inlines).start()
@bot.message_handler(commands=['stats'])
def stats(m) :
    if m.from_user.id == admin :
        bot.send_message(m.chat.id, redis.scard('RJ:users'))
@bot.message_handler(commands=['forward'])
def forward(m) :
    if m.from_user.id == admin :
        m = bot.send_message(m.chat.id, "متن مورد نظر خود را ارسال کنید\nبرای لغو عملیات /start را ارسال کنید...")
        bot.register_next_step_handler(m, forwarder)
def forwarder(m) :
    def forwarders() :
        if m.from_user.id == admin and m.text != '/start' :
            users = redis.smembers('RJ:users')
            n = 0
            for i in users :
                try :
                    bot.forward_message(i, m.chat.id, m.message_id)
                    n = n+1
                except :
                    pass
            bot.send_message(m.chat.id, "پیام به {} کاربر ارسال شد".format(n))
    Thread(target=forwarders).start()
@bot.message_handler(commands=['help'])
def adminhelp(m) :
    if m.from_user.id == admin :
        bot.send_message(m.chat.id, """فرم کلی تنظیم متن بصورت زیر است :
/set <attr> <text>
بجای <attr> میتوانید مقادیر زیر را قرار دهید :
start :
برای تنظیم متن شروع
help :
برای تنظیم راهنمای کاربران
link :
برای تنظیم لینک کانال
contact :
برای تنظیم متن ارتباط با ما
بجای <text> هم متن مورد نظر را قرار دهید
مثال :
/set start به ربات خوش آمدید
برای تغییر متن شروع ربات به :
به ربات خوش آمدید""")
@bot.message_handler(commands=['set'])
def set(m) :
    try :
        if m.from_user.id == admin :
            attr = m.text.split(' ')[1]
            text = m.text.replace('/set '+attr+' ', '')
            redis.set('RJ:contents:'+attr, text)
            bot.send_message(m.chat.id, "متن جدید تنظیم شد")
    except :
        bot.send_message(m.chat.id, "مشکلی در تغییر متن پیش آمده")
bot.polling()
