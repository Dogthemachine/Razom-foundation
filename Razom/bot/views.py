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


@bot.message_handler(commands=["letsfuck"])
def handle_letsfuck_command(message):
    bot.send_message(message.chat.id, "Збочинець!")


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):
    # button_text = "Продовжити"
    # button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='firststep')
    # keyboard = telebot.types.InlineKeyboardMarkup()
    # keyboard.row_width = 2
    # keyboard.add(button)
    # bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    button = telebot.types.KeyboardButton('Продовжити')
    keyboard.add(button)

    bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):

    if call.data == 'Продовжити':
        bot.send_message(call.message.chat.id, "Зараз ми вас зареэструэмо!")



# @bot.callback_query_handler(func=lambda call: call.data == 'firststep')
# def handle_button_click(call):
#     button_text = "Зареєструватись"
#     button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     keyboard.add(button)
#     bot.send_message(call.message.chat.id, answer.call_for_registration_message, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):
    string = message.text
    string = "Ок, " + string + ", не маю зауважень"
    bot.send_message(message.chat.id, string)
