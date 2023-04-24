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
        except:
            return HttpResponse(status=403)
        if update.message and update.message.text:
            bot.process_new_messages([update.message])
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    print("\n\n\n")
    print("(@bot.callback_query_handler(func=lambda call: True)")
    bot.send_message(call.message.chat.id, call.data)


@bot.message_handler(commands=["letsfuck"])
def handle_letsfuck_command(message):
    bot.send_message(message.chat.id, "Збочинець!")


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):

    button_text = "Продовжити"
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='first')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(button)

    bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):
    string = message.text
    string = "Ок, " + string + ", не маю зауважень"
    bot.send_message(message.chat.id, string)

