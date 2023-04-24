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

        print("\n\n\n")
        print("IF POST")
        print("\n\n\n")

        try:
            json_string = request.body.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)

            print("\n\n\n")
            print("update = telebot.types.Update.de_json(json_string)")
            print("\n\n\n")

        except:

            print("\n\n\n")
            print("return HttpResponse(status=403)")
            print("\n\n\n")

            return HttpResponse(status=403)

        if update.message and update.message.text:
            bot.process_new_messages([update.message])

            print("\n\n\n")
            print("bot.process_new_messages([update.message])")
            print("\n\n\n")

        print("\n\n\n")
        print("return HttpResponse(status=200)")
        print("\n\n\n")

        return HttpResponse(status=200)
    else:

        print("\n\n\n")
        print("return HttpResponse(status=403)")
        print("\n\n\n")

        return HttpResponse(status=403)


@bot.callback_query_handler(func=lambda message: True)
def callback_inline(call):

    print("\n\n\n")
    print("BUTTON")
    print("\n\n\n")

    bot.send_message(call.message.chat.id, call.data)


@bot.message_handler(commands=["letsfuck"])
def handle_letsfuck_command(message):

    print("\n\n\n")
    print("COMMAND")
    print("\n\n\n")

    bot.send_message(message.chat.id, "Збочинець!")


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):

    print("\n\n\n")
    print("START")
    print("\n\n\n")


    button_text = "Продовжити"
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='first')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(button)

    bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):

    print("\n\n\n")
    print("TEXT")
    print("\n\n\n")

    string = message.text
    string = "Ок, " + string + ", не маю зауважень"
    bot.send_message(message.chat.id, string)

