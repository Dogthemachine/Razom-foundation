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
    print("FIRST")
    print("\n\n\n")

    button_text = "Продовжити"
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='first_step')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(button)

    bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)


def callback_query(call):

    print("\n\n\n")
    print("BEFORE IF")
    print("\n\n\n")

    if call.data == "first_step":

        print("\n\n\n")
        print("ANSWER")
        print("\n\n\n")
        button_text = "Зареєструватись"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.answer_callback_query(call.id, answer.call_for_registration_message, reply_markup=keyboard)


@bot.inline_handler(func=lambda query: True)
def inline(query):
    keyboard = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="Button text", callback_data="inline")
    keyboard.add(btn)
    r = telebot.types.InlineQueryResultArticle(
        id="1",
        title="Title",
        input_message_content=telebot.types.InputTextMessageContent(message_text="Test"),
        reply_markup=keyboard
    )
    bot.answer_inline_query(query.id, [r], cache_time=10)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "inline":
        print(call)