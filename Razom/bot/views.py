from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address, Messages

import environ
import telebot
from telebot import types
from datetime import datetime
from pprint import pprint

env = environ.Env()
environ.Env.read_env()
bot = telebot.TeleBot(settings.TOKEN, threaded=False)
answer = Messages.objects.all().latest("id")


@csrf_exempt
def BasicBotView(request):

    if request.method == "POST" and request.content_type == "application/json":
        try:
            json_string = request.body.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return HttpResponse(status=200)

        except:
            return HttpResponse(status=403)


@bot.callback_query_handler(func=lambda callback_query: True)
def callback_inline(callback_query):

    if callback_query.data == "first":

        button_text = "Зареєструватись"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.send_message(callback_query.message.chat.id, answer.call_for_registration_message, reply_markup=keyboard)


@bot.message_handler(commands=["letsfuck"])
def handle_letsfuck_command(message):

    bot.send_message(message.chat.id, "Збочинець!")


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):

    try:
        chat = Chat.objects.get(chat_id=message.chat.id)

        print("\n\n\n")
        print("chat exist!")
        print("chat.status")
        print(chat.status)
        print("\n")
        print("message.chat")
        print(message.chat)
        print("\n\n\n")

        if chat.status == Chat(choises=WELCOME_MESSAGE):

            button_text = "Зареєструватись"
            button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button)

            bot.send_message(callback_query.message.chat.id, answer.call_for_registration_message, reply_markup=keyboard)

            chat.status = Chat(choises=REGISTRATION_START)
            chat.save()

    except:
        print("\n\n\n")
        print("chat don't exist!")
        print("\n")

        chat = Chat(chat_id=message.chat.id)

        print("\n")
        print("cat created!")

        chat.status = Chat(choises=WELCOME_MESSAGE)
        print("\n")
        print("cat.status=WELCOME_MESSAGE")
        print(chat.status)
        print("\n\n\n")

        button_text = "Продовжити"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='first')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)

        chat.save()


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):

    string = message.text
    string = "Ок, " + string + ", не маю зауважень"
    bot.send_message(message.chat.id, string)

