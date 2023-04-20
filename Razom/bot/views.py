from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from bot.models import Recipients, Volunteers, Feedbacks, Requests, Categories, Address, Messages

import environ
import telebot
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
    bot.send_message(message.chat.id, answer.welcome_message)

    # Create the inline keyboard and add the button
    message_text = answer.call_for_registration_message
    button_text = "Rregistration"
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='registration')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button)

    # Send the message to the user
    bot.send_message(message.chat.id, message_text, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):
    if message.text == "Lets print":
        bot.send_message(message.chat.id, "Now we will print request")
        bot.send_message(message.chat.id, message.welcome_message)
        bot.send_message(message.chat.id, "And now message")
        bot.send_message(message.chat.id, message)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    if call.data == 'registration':
        # Do something when the user presses the "Cats" button
        bot.send_message(call.message.chat.id, 'Now we will register you!')



# @telegram_bot.message_handler(func=lambda message: True, content_types=["text"])
# def telegram_message(message):
#     try:
#         chat = Chat.objects.get(chat_id=message.chat.id)
#     except Chat.DoesNotExist:
#         chat = Chat()
#         chat.chat_id = message.chat.id
#         chat.last_search = message.text
#         chat.telegram = True
#         chat.save()
#     if message.text == "Lets print":
#         if chat.subscription:
#             unsub_msg = "Вы были автоматически отписаны от предыдущей рассылки."
#             telegram_bot.send_message(chat.chat_id, unsub_msg)
#         chat.last_search = message.text
#         chat.subscription = False
#         chat.shown_vacancies = ""
#         chat.shown_image_vacancies = ""
#         chat.save()
#
#     m = reply(chat)
#     # m, i = reply(chat)
#
#     if m:
#         telegram_bot.send_message(chat.chat_id, m)
#     # if i:
#     #     telegram_bot.send_message(chat.chat_id, i)
#     if m:
#     # if m or i:
#         sub_msg = "Для получения автоматических обновлений введите /subscribe"
#         telegram_bot.send_message(chat.chat_id, sub_msg)




