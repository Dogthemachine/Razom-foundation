from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address, Messages, Chat, Subcategories

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

    if callback_query.data == "requests_button":
        try:
            print("\n\n\n")
            print("if callback_query.data == requests_button:")
            print("\n\n\n")

            recipient = Recipients.objects.get(chat_id=callback_query.message.chat.id)

            print("\n\n\n")
            print("recipient = Recipients.objects.get(chat_id=message.chat.id)")
            print("\n\n\n")

            all_requests = Requests.objects.filter(recipient=recipient)

            print("\n\n\n")
            print("all_requests = Requests.objects.filter(recipient=recipient)")
            print("\n\n\n")

            keyboard = telebot.types.InlineKeyboardMarkup()

            print("\n\n\n")
            print("keyboard = telebot.types.InlineKeyboardMarkup()")
            print("\n\n\n")

            for request in all_requests:

                print("\n\n\n")
                print("for request in all_requests:")
                print("\n\n\n")

                btn_txt = request.added.strftime("%d.%m.%Y")

                print("\n\n\n")
                print("btn_txt = request.date.strftime(%d.%m.%Y)")
                print("\n\n\n")

                callbackdata = "request_" + str(request.id)

                print("\n\n\n")
                print("callbackdata = request_ + str(request.id)")
                print("\n\n\n")

                btn = telebot.types.InlineKeyboardButton(text=btn_txt, callback_data=callbackdata)

                print("\n\n\n")
                print("btn = telebot.types.InlineKeyboardButton(text=btn_txt, callback_data=callbackdata)")
                print("\n\n\n")

                keyboard.add(btn)

                print("\n\n\n")
                print("keyboard.add(btn)")
                print("\n\n\n")

            bot.send_message(callback_query.message.chat.id, "Мої запити", reply_markup=keyboard)

            print("\n\n\n")
            print("bot.send_message(callback_query.message.chat.id, Мої запити, reply_markup=keyboard)")
            print("\n\n\n")

            chat.status = Chat.LIST_OF_REQUESTS

            print("\n\n\n")
            print("chat.status = Chat.LIST_OF_REQUESTS")
            print("\n\n\n")

            chat.save()

            print("\n\n\n")
            print("hat.save()")
            print("\n\n\n")

        except:
            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(callback_query.message.chat.id, answer.choice_message, reply_markup=keyboard)
            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()

    if callback_query.data.startswith('delete'):
        request_id = call.data.split('_')[2]
        try:
            request = Requests.objects.get(id=int(request_id))
            request.delete()
            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(callback_query.message.chat.id, answer.deletion_message, reply_markup=keyboard)
            chat.status = Chat.REQUEST_WAS_DELETED
            chat.save()
        except:
            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(callback_query.message.chat.id, answer.choice_message, reply_markup=keyboard)
            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()

    if callback_query.data.startswith('request'):
        request_id = call.data.split('_')[1]
        try:
            request = Requests.objects.get(id=int(request_id))
            reply = str(request.added) + "\n"
            reply += str(request.category) + "\n"
            reply += str(request.subcategory) + "\n"
            reply += str(request.comment) + "\n"
            reply += str(request.status) + "\n"
            reply += str(request.photo) + "\n"

            keyboard = telebot.types.InlineKeyboardMarkup()
            btn_del_txt = "Видалити"
            btn_back_txt = "Назад"
            btn_back_callbackdata = "continue"
            btn_del_callbackdata = "delete_request_" + str(request.id)
            btn_del = telebot.types.InlineKeyboardButton(text=btn_del_txt, callback_data=btn_del_callbackdata)
            btn_back = telebot.types.InlineKeyboardButton(text=btn_back_txt, callback_data=btn_back_callbackdata)
            keyboard.add(btn_del)
            keyboard.add(btn_back)
            bot.send_message(callback_query.message.chat.id, reply, reply_markup=keyboard)
            chat.status = Chat.LIST_OF_REQUESTS
            chat.save()
        except:
            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(callback_query.message.chat.id, answer.choice_message, reply_markup=keyboard)
            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()

    if callback_query.data == "continue":

        help_button = "Запит на допомогу"
        requests_button = "Мої запити"
        button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
        button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button_1)
        keyboard.add(button_2)
        bot.send_message(callback_query.message.chat.id, answer.successful_registration_message, reply_markup=keyboard)
        chat.status = Chat.REGISTRATION_COMPLETE
        chat.save()

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

    if callback_query.data == "help_button":

        food_button = "Продукти харчування"
        repair_button = "Ремонт"
        button_1 = telebot.types.InlineKeyboardButton(text=food_button, callback_data='food_button')
        button_2 = telebot.types.InlineKeyboardButton(text=repair_button, callback_data='repair_button')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button_1)
        keyboard.add(button_2)
        bot.send_message(callback_query.message.chat.id, answer.select_category_message, reply_markup=keyboard)
        chat.status = Chat.SELECT_CATEGORY
        chat.save()

    if callback_query.data == "food_button":

        grocery_set_button = "Продуктовий набір"
        pet_food_button = "Корм для тварин"
        baby_food_button = "Дитяче харчування"
        button_1 = telebot.types.InlineKeyboardButton(text=grocery_set_button, callback_data='grocery_set_button')
        button_2 = telebot.types.InlineKeyboardButton(text=pet_food_button, callback_data='pet_food_button')
        button_3 = telebot.types.InlineKeyboardButton(text=baby_food_button, callback_data='baby_food_button')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button_1)
        keyboard.add(button_2)
        keyboard.add(button_3)
        bot.send_message(callback_query.message.chat.id, "Виберіть категорію:", reply_markup=keyboard)

        chat.status = Chat.FOOD_CATEGORIES
        chat.save()

    if callback_query.data == "repair_button":

        bot.send_message(callback_query.message.chat.id, "Вкажіть будь-ласка який бюджет потрібно для ремонтних робіт")

        chat.status = Chat.REPAIR_BUDGET
        chat.save()

    if callback_query.data == "grocery_set_button" or callback_query.data == "pet_food_button" or callback_query.data == "baby_food_button":
        request = Requests()
        request.recipient = Recipients.objects.get(chat_id=callback_query.message.chat.id)
        request.chat_id = callback_query.message.chat.id
        food_cat = Categories.objects.get(index="1")
        request.category = food_cat
        if callback_query.data == "grocery_set_button":
            sub_cat = Subcategories.objects.get(index="1")
            request.sub_category = sub_cat
        elif callback_query.data == "pet_food_button":
            sub_cat = Subcategories.objects.get(index="2")
            request.sub_category = sub_cat
        elif callback_query.data == "baby_food_button":
            sub_cat = Subcategories.objects.get(index="3")
            request.sub_category = sub_cat
        request.date = datetime.now()
        request.status = "Cтворений"
        request.save()
        bot.send_message(callback_query.message.chat.id, answer.request_help_comment_message)
        chat.open_request = request
        chat.status = Chat.REQUEST_COMMENT_MESSAGE
        chat.save()


@bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):

    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
        try:
            recipient = Recipients.objects.get(chat_id=message.chat.id)

            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(message.chat.id, answer.choice_message, reply_markup=keyboard)

            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()


        except:

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
        if pattern.match(string):
            name, surname = string.split()

            try:
                recipient = Recipients.objects.get(chat_id=message.chat.id)
            except:
                recipient = Recipients()

            recipient.name = name
            recipient.surname = surname
            recipient.save()

            bot.send_message(message.chat.id, answer.call_for_bday_message)
            chat.status = Chat.SETTING_DATE_OF_BRTH
            chat.save()

        else:
            reply = "Введіть ім'я та прізвище двома окремими словами, кожен з великої літери"
            bot.send_message(message.chat.id, reply)

    elif chat.status == Chat.SETTING_DATE_OF_BRTH:

        pattern = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
        if pattern.match(string):

            try:
                recipient = Recipients.objects.get(chat_id=message.chat.id)
            except:
                recipient = Recipients()

            date_of_birth = datetime.strptime(string, '%d.%m.%Y').date()
            recipient.date_of_birth = date_of_birth
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

            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(message.chat.id, answer.successful_registration_message, reply_markup=keyboard)

            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()

        else:
            reply = "Введіть правильну електронну пошту"
            bot.send_message(message.chat.id, reply)

    elif chat.status == Chat.REQUEST_COMMENT_MESSAGE:
        try:
            request = chat.open_request
            request.comment = string
            request.save()

            button = telebot.types.InlineKeyboardButton(text="Продовжити", callback_data='continue')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button)
            bot.send_message(message.chat.id, answer.save_request_message, reply_markup=keyboard)
            chat.status = Chat.REQUEST_SAVED
            chat.open_request = None
            chat.save()

        except:
            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1, button_2)
            bot.send_message(message.chat.id, answer.choice_message, reply_markup=keyboard)
            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()

    elif chat.status == Chat.REPAIR_BUDGET:
        try:
            request = Requests()
            request.recipient = Recipients.objects.get(chat_id=message.chat.id)
            request.chat_id = message.chat.id
            repair_cat = Categories.objects.get(index="2")
            request.category = repair_cat
            request.comment = "Запитана сума на ремонт: " + string
            request.date = datetime.now()
            request.status = "Cтворений"
            request.save()

            bot.send_message(message.chat.id, "Тепер будь ласка сфотографуйте те, що потрібно відремонтувати")
            chat.open_request = request
            chat.status = Chat.LEAVE_REPAIR_PHOTO
            chat.save()

        except:
            help_button = "Запит на допомогу"
            requests_button = "Мої запити"
            button_1 = telebot.types.InlineKeyboardButton(text=help_button, callback_data='help_button')
            button_2 = telebot.types.InlineKeyboardButton(text=requests_button, callback_data='requests_button')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(button_1)
            keyboard.add(button_2)
            bot.send_message(message.chat.id, answer.choice_message, reply_markup=keyboard)
            chat.status = Chat.REGISTRATION_COMPLETE
            chat.save()


@bot.message_handler(func=lambda message: True, content_types=["photo"])
def handle_photo(message):
    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
        request = chat.open_request
        photo_array = message.photo
        largest_photo = photo_array[-1]
        file_id = largest_photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = settings.MEDIA_ROOT + "/requests_images/" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".jpg"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        request.photo = file_path
        request.save()

        bot.send_message(message.chat.id, answer.request_help_comment_message)
        chat.status = Chat.REQUEST_COMMENT_MESSAGE
        chat.save()

    except:
        pass

