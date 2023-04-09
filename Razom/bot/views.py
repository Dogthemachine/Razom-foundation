from django.views import View
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address

import environ
import telebot

env = environ.Env()
environ.Env.read_env()
telegram_bot = telebot.TeleBot(settings.TOKEN, threaded=False)

# class BasicBotView(View):
#     def get(self, request):
#
#             request,
#             "page.html", {},
#         )


# @csrf_exempt
# class BasicBotView(View):
#     @bot.message_handler(commands=['start', 'help'])
#     def send_welcome(message):
#         bot.reply_to(message, "Слава Україні!")
#
#     @bot.message_handler(func=lambda message: True)
#     def echo_all(message):
#         bot.reply_to(message, message.text)
#
#     bot.infinity_polling()

class BasicBotView(View):
    def post(request):
        if request.method == "POST" and request.content_type == "application/json":
            try:
                json_string = request.body.decode("utf-8")
                update = telebot.types.Update.de_json(json_string)
            except:
                return HttpResponse(status=403)
            if update.message and update.message.text:
                telegram_bot.process_new_messages([update.message])
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)


@telegram_bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):
    telegram_bot.send_message(message.chat.id, "Слава Україні!")