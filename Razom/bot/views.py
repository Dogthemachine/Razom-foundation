from django.views import View
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address

import environ
import telebot

env = environ.Env()
environ.Env.read_env()
bot = telebot.TeleBot(settings.TOKEN)

class BasicBotView(View):
    def get(self, request):
        if request.method == "POST":
            update = telebot.types.Update.de_json(request.body.decode('utf-8'))
            bot.process_new_updates([update])

        return HttpResponse('<h1>Слава Україні!</h1>')
