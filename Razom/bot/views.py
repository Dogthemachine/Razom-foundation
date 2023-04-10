from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address

import environ
import telebot
from datetime import datetime

env = environ.Env()
environ.Env.read_env()
bot = telebot.TeleBot(settings.TOKEN, threaded=False)



def BasicBotView(self, request):
    print("\n\n", "TEST", "\n\n")
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


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):
    telegram_bot.send_message(message.chat.id, "Слава Україні!")


@bot.message_handler(commands=["Героям слава!"])
def telegram_welcome(message):
    telegram_bot.send_message(message.chat.id, "Русні пізда")