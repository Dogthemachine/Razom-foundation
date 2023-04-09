from django.views import View
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address

import environ
import telebot
from datetime import datetime


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


def BasicBotView(request):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    telegram_bot = telebot.TeleBot(settings.TOKEN, threaded=False)

    with open(settings.MEDIA_ROOT + "/log.txt", 'w') as file:
        file.write(f"{now}: In the BasicBotView but before post function\n")
        file.write(settings.TOKEN)

    if request.method == "POST" and request.content_type == "application/json":
        try:
            json_string = request.body.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
        except:
            return HttpResponse(status=403)
        if update.message and update.message.text:
            telegram_bot.process_new_messages([update.message])

        with open(settings.MEDIA_ROOT + "/log.txt", 'w') as file:
            file.write(f"{now}: Status=200\n")

        return HttpResponse(status=200)
    else:

        with open(settings.MEDIA_ROOT + "/log.txt", 'w') as file:
            file.write(f"{now}: status=403\n")

        return HttpResponse(status=403)


@telegram_bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):
    telegram_bot.send_message(message.chat.id, "Слава Україні!")