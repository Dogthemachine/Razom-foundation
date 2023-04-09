from django.views import View
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address

import environ
import telebot

env = environ.Env()
environ.Env.read_env()
tbot = telebot.AsyncTeleBot(settings.TOKEN)

@csrf_exempt
class BasicBotView(View):
    def get(self, request):
        if request.META['CONTENT_TYPE'] == 'application/json':

            json_data = request.body.decode('utf-8')
            update = telebot.types.Update.de_json(json_data)
            tbot.process_new_updates([update])

            return HttpResponse("")

        else:
            raise PermissionDenied


@tbot.message_handler(commands=['start'])
def greet(m):
    tbot.send_message(m.chat.id, "Hello")




# class BasicBotView(View):
#     def get(self, request):
#
#         return render(
#             request,
#             "page.html", {},
#         )
