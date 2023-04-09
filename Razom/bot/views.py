from django.views import View
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address

import environ
import telebot

env = environ.Env()
environ.Env.read_env()
bot = telebot.AsyncTeleBot(settings.TOKEN)

# class BasicBotView(View):
#     def get(self, request):
#
#         return render(
#             request,
#             "page.html", {},
#         )



class BasicBotView(View):
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Howdy, how are you doing?")

    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        bot.reply_to(message, message.text)

    bot.infinity_polling()