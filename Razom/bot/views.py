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


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):

    print("\n\n\n")
    print("INSIDE telegram_welcome")
    print("\n\n\n")

    button_text = "Продовжити"
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='first_step')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(button)

    bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)


@bot.inline_handler(func=lambda query: True)
def inline(query):
    print("\n\n\n")
    print("INSIDE inline_handler PRINTING query:")
    print(query)
    print("\n\n\n")

    button_text = "Test button"
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='test_button')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(button)

    bot.send_message(message.chat.id, "Test message from inline_handler", reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    print("\n\n\n")
    print("INSIDE def callback_query(call):")
    print("\n\n\n")

    if call.data == "first_step":

        print("\n\n\n")
        print("CALL")
        print(call)
        print("\n\n\n")

        button_text = "Зареєструватись"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.answer_callback_query(call.id, answer.call_for_registration_message, reply_markup=keyboard)

    if call.data == "test_button":
        bot.answer_callback_query(call.id, "test answer")


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):
    string = message.text
    string = "Ок, " + string + ", немаю зауважень"
    bot.send_message(message.chat.id, string)


@bot.message_handler(commands=["lets_fuck"])
def telegram_channels(message):
    bot.send_message(message.chat.id, "Збочинець!")


print("\n\n\n")
print("print in view")
print("\n\n\n")
