from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address, Messages, Chat

import re
import environ
import telebot
from telebot import types
from datetime import datetime
from pprint import pprint

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
            bot.process_new_updates([update])
            return HttpResponse(status=200)

        except:
            return HttpResponse(status=403)


@bot.callback_query_handler(func=lambda callback_query: True)
def callback_inline(callback_query):

    try:
        chat = Chat.objects.get(chat_id=callback_query.message.chat.id)

    except:
        chat = Chat(chat_id=callback_query.message.chat.id)
        chat.status = Chat.WELCOME_MESSAGE

    if callback_query.data == "first":

        button_text = "Зареєструватись"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.send_message(callback_query.message.chat.id, answer.call_for_registration_message, reply_markup=keyboard)
        chat.status = Chat.REGISTRATION_START
        chat.save()

    if callback_query.data == "register":

        bot.send_message(callback_query.message.chat.id, answer.call_for_phone_message)
        chat.status = Chat.SETTING_PHONE
        chat.save()




@bot.message_handler(commands=["letsfuck"])
def handle_letsfuck_command(message):

    bot.send_message(message.chat.id, "Збочинець!")


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):

    try:
        chat = Chat.objects.get(chat_id=message.chat.id)

        button_text = "Зареєструватись"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='register')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.send_message(message.chat.id, answer.call_for_registration_message, reply_markup=keyboard)
        chat.status = Chat.REGISTRATION_START
        chat.save()

    except:
        chat = Chat(chat_id=message.chat.id)
        chat.status = Chat.WELCOME_MESSAGE

    if chat.status == Chat.WELCOME_MESSAGE:

        button_text = "Продовжити"
        button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='first')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)

        bot.send_message(message.chat.id, answer.welcome_message, reply_markup=keyboard)
        chat.status = Chat.REGISTRATION_START
        chat.save()


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):

    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
    except:

        chat = Chat(chat_id=message.chat.id)
        chat.status = Chat.WELCOME_MESSAGE

    string = message.text

    if chat.status == Chat.SETTING_PHONE:

        pattern = re.compile(r'^\d{10}$')

        if pattern.match(string):

            try:
                recipient = Recipients.objects.get(chat_id=message.chat.id)
            except:
                recipient = Recipients()

            recipient.chat_id = message.chat.id

            login_name = message.chat.first_name + "_" + message.chat.last_name

            recipient.login_name = login_name

            recipient.phone_number = string

            recipient.save()

            chat.recipient = recipient

            bot.send_message(message.chat.id, answer.call_for_name_surname_message)
            chat.status = Chat.SETTING_NAME_SURNAME
            chat.save()

        else:
            reply = "Будь ласка, введіть номер телефону з десяти цифр, без пробілів"
            bot.send_message(message.chat.id, reply)


    elif chat.status == Chat.SETTING_NAME_SURNAME:

        pattern = re.compile(r'^[А-ЩЬЮЯҐЄІЇа-щьюяґєії]+\s[А-ЩЬЮЯҐЄІЇа-щьюяґєії]+$')

        print("\n\n\n")
        print("chat.status == Chat.SETTING_NAME_SURNAME:")
        print("Users input:")
        print(string)
        print("\n\n\n")

        if pattern.match(string):
            name, surname = string.split()

            print("\n\n\n")
            print("if pattern.match(string):")
            print("\n\n\n")

            try:
                recipient = Recipients.objects.get(chat_id=message.chat.id)
            except:
                recipient = Recipients()

            print("\n\n\n")
            print("recipient = Recipients.objects.get(chat_id=message.chat.id)")
            print("\n\n\n")

            recipient.name = name

            print("\n\n\n")
            print("recipient.name = name")
            print("\n\n\n")

            recipient.surname = surname

            print("\n\n\n")
            print("recipient.surname = surname")
            print("\n\n\n")

            recipient.save()

            print("\n\n\n")
            print("recipient.save()")
            print("\n\n\n")

            bot.send_message(message.chat.id, answer.call_for_bday_message)

            print("\n\n\n")
            print("bot.send_message(message.chat.id, answer.call_for_bday_message)")
            print("\n\n\n")

            chat.status = Chat.SETTING_DATE_OF_BRTH

            print("\n\n\n")
            print("chat.status = Chat.SETTING_DATE_OF_BRTH")
            print("\n\n\n")

            chat.save()

            print("\n\n\n")
            print("chat.save()")
            print("\n\n\n")

        else:
            reply = "Введіть ім'я та прізвище двома окремими словами, кожен з великої літери"

            print("\n\n\n")
            print("Введіть ім'я та прізвище двома окремими словами, кожен з великої літери")
            print("\n\n\n")

            bot.send_message(message.chat.id, reply)

            print("\n\n\n")
            print("bot.send_message(message.chat.id, reply)")
            print("\n\n\n")

    elif chat.status == Chat.SETTING_DATE_OF_BRTH:

        pattern = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')

        if pattern.match(string):
            try:
                recipient = Recipients.objects.get(chat_id=message.chat.id)
            except:
                recipient = Recipients()

            recipient.date_of_birth = string
            recipient.save()

            bot.send_message(message.chat.id, answer.call_for_address_message)
            chat.status = Chat.SETTING_ADRESS
            chat.save()

        else:
            reply = "Введіть дату у форматі [дд.мм.рррр]"
            bot.send_message(message.chat.id, reply)

    elif chat.status == Chat.SETTING_ADRESS:

        try:
            recipient = Recipients.objects.get(chat_id=message.chat.id)
        except:
            recipient = Recipients()

        recipient.address = string
        recipient.save()

        bot.send_message(message.chat.id, answer.call_for_email_message)
        chat.status = Chat.SETTING_EMAIL
        chat.save()

    elif chat.status == Chat.SETTING_EMAIL:
        pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if pattern.match(string):
            try:
                recipient = Recipients.objects.get(chat_id=message.chat.id)
            except:
                recipient = Recipients()
            recipient.email = string
            recipient.save()

            bot.send_message(message.chat.id, answer.successful_registration_message)
            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()

        else:
            reply = "Введіть правильну електронну пошту"
            bot.send_message(message.chat.id, reply)

