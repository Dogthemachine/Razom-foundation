# -*- coding: utf-8 -*-
import json
import telebot
import random
import string
import datetime
import re

from viberbot import Api
from datetime import timedelta
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages import PictureMessage
from viberbot.api.viber_requests import (
    ViberConversationStartedRequest,
    ViberMessageRequest,
)
from django.http import HttpResponse
from django.template import defaultfilters
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login
from django.utils import timezone

from .models import (
    Chat,
    BotQuery,
    VacancyQuestionnaire,
    ViberResponseDialog,
    ViberDialog,
    ViberLinkKey,
    ResponseForVacancy,
    BotTransitions,
)
from .search import search
from .helpers import string_to_crmid, viber_keyboard
from .helpers import EMPLOYRE_GREETINGS

from apps.helpers import normalize_phones
from apps.companies.models import Company
from apps.profiles.models import JobBoardUser
from apps.runtime_config.models import Config
from apps.vacancies.models import Vacancy
from apps.categories.models import Category


config = Config.objects.all().latest("id")
telegram_bot = telebot.TeleBot(config.telegram_bot_token, threaded=False)
viber_bot = Api(
    BotConfiguration(
        name="NaRabotu_Bot",
        avatar="https://narabotu.od.ua/media/icons/000.jpg",
        auth_token=config.viber_bot_token,
    )
)
# import logging
# telebot.logger.setLevel(logging.DEBUG)


def reply(chat):
    msg = ""
    # image_msg = ""
    search_result, vacancies_tail = search(chat.last_search, chat.shown_vacancies)
    chat.last_search_tail = vacancies_tail

    for i in search_result:
        if i.phones:
            msg += (
                i.vacancy
                + "\n"
                + defaultfilters.truncatewords(strip_tags(i.description), 10)
                + "\n"
                + ", ".join(['+' + str(x) for x in i.phones])
                + "\n"
                + "https://narabotu.od.ua/vacancy/"
                + str(i.id)
                + "\n\n"
                    )
        chat.shown_vacancies += str(i.id) + ","
    #
    # for i in search(
    #     chat.last_search,
    #     chat.shown_image_vacancies,
    #     image_vacancies=True,
    # ):
    #     image_msg += i.image_url()
    #     chat.shown_image_vacancies += str(i.id) + ","

    if not msg:
    # if not msg and not image_msg:
        msg = "Извините, ничего подходящего сейчас нет\n\n"
        chat.more = False
        if chat.telegram:
            msg += "Чтобы посмотреть все каналы введите /channels"
        elif chat.viber:
            # msg += 'Чтобы посмотреть все паблик-аккаунты введите "паблики" (без кавычек).'
            msg += config.viber_pa_msg
    else:
        if chat.telegram:
            msg += "\nДля дополнительных результатов введите /more"
        # elif chat.viber:
        #     msg += '\nДля дополнительных результатов введите "ещё" (без кавычек).'

    chat.save()

    return msg
    # return msg, image_msg


def telegram_webhook(request):
    if request.method == "POST" and request.content_type == "application/json":
        try:
            json_string = request.body.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
        except:
            return HttpResponse(status=403)
        if update.message and update.message.text:
            stat = BotQuery()
            stat.telegram = True
            stat.vacancy = update.message.text[:128]
            stat.save()
            telegram_bot.process_new_messages([update.message])
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


@telegram_bot.message_handler(commands=["help", "start"])
def telegram_welcome(message):
    telegram_bot.send_message(message.chat.id, config.telegram_welcome_msg)


@telegram_bot.message_handler(commands=["channels"])
def telegram_channels(message):
    telegram_bot.send_message(message.chat.id, config.telegram_channels_msg)


@telegram_bot.message_handler(commands=["subscribe", "sub"])
def telegram_channels(message):
    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
    except Chat.DoesNotExist:
        telegram_bot.send_message(message.chat.id, "Введите поисковой запрос")

    chat.subscription = True
    chat.save()

    telegram_bot.send_message(message.chat.id, "Вы подписались на рассылку обновлений")
    telegram_bot.send_message(
        message.chat.id,
        "Для того, чтобы отписаться от рассылки обновлений, введите /unsubscribe",
    )


@telegram_bot.message_handler(commands=["unsubscribe", "unsub"])
def telegram_channels(message):
    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
    except Chat.DoesNotExist:
        telegram_bot.send_message(message.chat.id, "Подписка на обновления не активна")

    chat.subscription = False
    chat.save()

    telegram_bot.send_message(message.chat.id, "Вы отписались от рассылки обновлений")


@telegram_bot.message_handler(commands=["more"])
def telegram_channels(message):
    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
    except Chat.DoesNotExist:
        telegram_bot.send_message(message.chat.id, "Введите поисковой запрос")

    m = reply(chat)
    # m, i = reply(chat)

    if m:
        telegram_bot.send_message(chat.chat_id, m)
    # if i:
    #     telegram_bot.send_message(chat.chat_id, i)
    if m:
    # if m or i:
        sub_msg = "Для получения автоматических обновлений введите /subscribe"
        telegram_bot.send_message(chat.chat_id, sub_msg)


@telegram_bot.message_handler(func=lambda message: True, content_types=["text"])
def telegram_message(message):
    try:
        chat = Chat.objects.get(chat_id=message.chat.id)
    except Chat.DoesNotExist:
        chat = Chat()
        chat.chat_id = message.chat.id
        chat.last_search = message.text
        chat.telegram = True
        chat.save()
    if not chat.last_search == message.text:
        if chat.subscription:
            unsub_msg = "Вы были автоматически отписаны от предыдущей рассылки."
            telegram_bot.send_message(chat.chat_id, unsub_msg)
        chat.last_search = message.text
        chat.subscription = False
        chat.shown_vacancies = ""
        chat.shown_image_vacancies = ""
        chat.save()

    m = reply(chat)
    # m, i = reply(chat)

    if m:
        telegram_bot.send_message(chat.chat_id, m)
    # if i:
    #     telegram_bot.send_message(chat.chat_id, i)
    if m:
    # if m or i:
        sub_msg = "Для получения автоматических обновлений введите /subscribe"
        telegram_bot.send_message(chat.chat_id, sub_msg)


def viber_chat(request, request_user):
    try:
        chat = Chat.objects.get(chat_id=request_user.id)
    except Chat.DoesNotExist:
        chat = Chat(
            chat_id=request_user.id,
            viber=True,
            status=Chat.INIT_CHAT,
            name=request_user.name,
        )
        chat.save()
        # if request_user.avatar:
        #     avatar_param = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(request_user.avatar).query))
        #     avatar_fl = avatar_param['dlid'] + '.' + avatar_param['fltp']
        #     r = requests.get(request_user.avatar, stream=True)
        #     f_vb = settings.MEDIA_ROOT + avatar_fl
        #     with open(f_vb, 'wb') as f:
        #         for chunk in r.iter_content(chunk_size=1024):
        #             if chunk:  # filter out keep-alive new chunks
        #                 f.write(chunk)
        #     chat.avatar = f_vb
        #     chat.save()
        #     os.remove(f_vb)
    user = JobBoardUser.objects.filter(viber_id=request_user.id).first()
    if not user:
        print("--- user add ---", request_user.id, request_user.name[:64])
        user = JobBoardUser(
            viber_id=request_user.id,
            first_name=request_user.name[:64],
            username=request_user.id,
        )
        user.save()
        chat.status = Chat.SEARCH
        chat.save()
    if not user.is_authenticated:
        login(request, user)
    return chat


def viber_webhook(request):
    if request.method == "POST":
        # if not viber.verify_signature(request.body, request.META.get('X-Viber-Content-Signature', '')):
        #    return HttpResponse(status=403)

        viber_request = viber_bot.parse_request(request.body.decode("utf-8"))
        # print('\n\n\n')
        # print(viber_request)
        # print('\n\n\n')

        if isinstance(viber_request, ViberConversationStartedRequest):
            chat = viber_chat(request, viber_request.user)

            if viber_request.context and viber_request.context[:7] == "vacancy":
                vac = viber_request.context[7:]
                try:
                    vacancy = Vacancy.objects.get(pk=vac)
                except:
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text="Internal error"), viber_keyboard()],
                    )
                    return HttpResponse(status=200)

                dialogs = ViberDialog.objects.filter(chat=chat, vacancy=vacancy)
                if dialogs and not dialogs[0].block:
                    chat.status = Chat.RESPONSE
                    chat.vacancy = dialogs[0].vacancy
                    mess = (
                        dialogs[0].get_name_last_dialog(messages=2)
                        + "\n\n"
                        + str(_("Your can send a message to the HR."))
                    )
                    chat.save()
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=mess), viber_keyboard(chat=chat)],
                    )
                    return HttpResponse(status=200)
                elif dialogs and dialogs[0].block:
                    chat.status = Chat.SELECTION
                    chat.save()
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [
                            TextMessage(
                                text=str(_("Dialog for vacancy has bin blocked."))
                            ),
                            viber_keyboard(chat=chat, dialogs=dialogs),
                        ],
                    )
                    return HttpResponse(status=200)
                dialog = ViberDialog(chat=chat, vacancy=vacancy)
                dialog.dialog = "~".join(
                    [
                        q.question
                        for q in VacancyQuestionnaire.objects.filter(
                            vacancy=vacancy
                        ).order_by("position")
                    ]
                )
                dialog.step = 0
                dialog.save()

                if chat.status == Chat.SEARCH:
                    question = str(_("Input your question, please."))
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=question), viber_keyboard()],
                    )
                    return HttpResponse(status=200)

                chat.status = Chat.ANSWER
                chat.save()
                return HttpResponse(status=200)

            elif viber_request.context and viber_request.context[:6] == "crm_id":

                crm_id = viber_request.context[6:]
                mes = EMPLOYRE_GREETINGS + '\n\nВведите "Начать"'
                bot_transitions = BotTransitions(viber=True, context_key='viber_welcome_msg',
                                                 context_data='')
                bot_transitions.save()
                chat.hr = int(crm_id)
                chat.status = Chat.EMPLOYER_START
                chat.save()
                viber_bot.send_messages(viber_request.user.id, [TextMessage(text=mes)])
                return HttpResponse(status=200)

            else:
                print(
                    chat.id,
                    "--------------------------------------------------<<<!!!>>>",
                )
                bot_transitions = BotTransitions(viber=True, context_key='viber_welcome_msg',
                                                 context_data='')
                bot_transitions.save()
                mess = config.viber_welcome_msg
                viber_bot.send_messages(viber_request.user.id, [TextMessage(text=mess)])
                # mess = config.viber_welcome_msg
                # if chat.status == Chat.INIT_CHAT:
                #    mess += '\n\n' + str(_('Input your name, please.'))
                # viber_bot.send_messages(viber_request.sender.id, [TextMessage(text=mess), viber_keyboard(chat=chat)])
                print(
                    chat.id,
                    "-------------------------------------------------->>>!!!<<<",
                )
                return HttpResponse(status=200)

        elif isinstance(viber_request, ViberMessageRequest):
            chat = viber_chat(request, viber_request.sender)
            user = JobBoardUser.objects.filter(viber_id=viber_request.sender.id).first()
            message = viber_request.message

            print('\n\n')
            print('message.text-->' + message.text +'<--')
            print('\n\n')

            if (
                viber_request.sender.id == "csKszIfHnt80GiGXoDbFaw=="
                and message.text == "Hi!"
            ):
                print("---------------------------------------------")
                print(viber_request.message)
                print(viber_request.sender)
                viber_bot.send_messages(
                    viber_request.sender.id,
                    [TextMessage(text=str(_("---Hi---"))), viber_keyboard(chat=chat)],
                )
                return HttpResponse(status=200)

            if chat.status == Chat.INIT_CHAT:
                chat.name = message.text[:128]
                if chat.vacancy:
                    chat.status = Chat.ANSWER
                    chat.save()
                else:
                    chat.status = Chat.SEARCH
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [
                            TextMessage(
                                text=str(_("Thank. Enter a vacancy to search."))
                            ),
                            viber_keyboard(),
                        ],
                    )
                    chat.save()
                    return HttpResponse(status=200)

            # --------------------------------------------------------------------------------- SEARCH
            elif chat.status == Chat.SEARCH:

                if (
                    message.text.lower() == "помощь"
                    or message.text.lower() == "помогите"
                ):
                    mes = config.viber_welcome_msg
                    if chat.more and chat.last_search:
                        mes += "(" + chat.last_search + ")"
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=mes), viber_keyboard(chat=chat)],
                    )

                elif (
                    message.text.lower() == "подписаться"
                    or message.text.lower() == "подписка"
                ):
                    if not chat.last_search:
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text="Введите поисковой запрос"),
                                viber_keyboard(chat=chat),
                            ],
                        )
                        return HttpResponse(status=200)
                    chat.subscription = True
                    chat.save()
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [
                            TextMessage(text="Вы подписались на рассылку обновлений"),
                            viber_keyboard(chat=chat),
                        ],
                    )

                elif (
                    message.text.lower() == "отписаться"
                    or message.text.lower() == "отписка"
                ):
                    chat.subscription = False
                    chat.save()
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [
                            TextMessage(text="Вы отписались от рассылки обновлений"),
                            viber_keyboard(chat=chat),
                        ],
                    )

                elif message.text.lower() == "еще" or message.text.lower() == "ещё":
                    if not chat.last_search:
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text="Введите поисковой запрос"),
                                viber_keyboard(chat=chat),
                            ],
                        )
                        return HttpResponse(status=200)
                    m = reply(chat)
                    # m, i = reply(chat)
                    message = []
                    if m:
                        message.append(TextMessage(text=m))
                    # if i:
                    #     message.append(PictureMessage(media=i))
                    message.append(viber_keyboard(chat=chat))
                    viber_bot.send_messages(chat.chat_id, message)

                elif message.text.lower() == "allvacancies":
                    dialogs = ViberDialog.objects.filter(chat=chat, block__isnull=True)
                    if dialogs.count() == 0:
                        chat.status = Chat.SEARCH
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("No active vacancies found."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                    elif dialogs.count() == 1:
                        chat.status = Chat.RESPONSE
                        chat.vacancy = dialogs[0].vacancy
                        mess = (
                            dialogs[0].get_name_last_dialog(messages=2)
                            + "\n\n"
                            + str(_("Your can send a message to the HR."))
                        )
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat)],
                        )
                    else:
                        chat.status = Chat.SELECTION
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(
                                    text=str(
                                        _(
                                            "Select the vacancy for which your want to send a message."
                                        )
                                    )
                                ),
                                viber_keyboard(chat=chat, dialogs=dialogs),
                            ],
                        )
                else:
                    stat = BotQuery()
                    stat.viber = True
                    stat.vacancy = message.text[:128]
                    stat.save()
                    if not chat.last_search == message.text:
                        if chat.subscription:
                            unsub_msg = (
                                "Вы были автоматически отписаны от предыдущей рассылки."
                            )
                            viber_bot.send_messages(
                                chat.chat_id, [TextMessage(text=unsub_msg)]
                            )
                    chat.last_search = message.text
                    chat.subscription = False
                    chat.shown_vacancies = ""
                    chat.more = True
                    chat.shown_image_vacancies = ""
                    chat.save()

                    m = reply(chat)
                    # m, i = reply(chat)
                    message = []
                    if m:
                        message.append(TextMessage(text=m))
                    # if i:
                    #     message.append(PictureMessage(media=i))
                    message.append(viber_keyboard(chat=chat))
                    viber_bot.send_messages(chat.chat_id, message)
            # --------------------------------------------------------------------------------- ANSWER
            elif chat.status == Chat.ANSWER:

                dialog = ViberDialog.objects.filter(
                    chat=chat, vacancy=chat.vacancy
                ).first()
                if not dialog or message.text.lower() == "search":
                    chat.status = Chat.SEARCH
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [
                            TextMessage(text=str(_("Enter vacancy for search."))),
                            viber_keyboard(chat=chat),
                        ],
                    )
                else:
                    response_dialog = ViberResponseDialog(
                        dialog=dialog, text=message.text, question=False
                    )
                    response_dialog.save()
                    questions = dialog.dialog.split("~")
                    if dialog.step and dialog.step < len(questions):
                        mess = questions[dialog.step]
                        dialog.step += 1
                        dialog.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat)],
                        )
                    elif dialog.step and dialog.step == len(questions):
                        dialog.step.dialog = None
                        dialog.step.step = None
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Ask a HR a question."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                    else:
                        dialog.step.dialog = None
                        dialog.step.step = None
                        chat.status = Chat.SEARCH
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Enter vacancy for search."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                    dialog.step.save()
                chat.save()

            # --------------------------------------------------------------------------------- RESPONSE
            elif chat.status == Chat.RESPONSE:
                dialogs = ViberDialog.objects.filter(chat=chat)
                if message.text == "allvacancies":
                    if dialogs.count() == 0:
                        chat.status = Chat.SEARCH
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("No active vacancies found."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                    elif dialogs.count() == 1:
                        chat.vacancy = dialogs[0].vacancy
                        mess = (
                            dialogs[0].get_name_last_dialog(messages=2)
                            + "\n\n"
                            + str(_("Your can send a message to the HR."))
                        )
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=mess),
                                viber_keyboard(chat=chat, dialogs=dialogs),
                            ],
                        )
                    else:
                        chat.status = Chat.SELECTION
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(
                                    text=str(
                                        _(
                                            "Select the vacancy for which your want to send a message."
                                        )
                                    )
                                ),
                                viber_keyboard(chat=chat),
                            ],
                        )
                elif message.text == "showdialog":
                    try:
                        dialog = ViberDialog.objects.filter(
                            chat=chat, vacancy=chat.vacancy
                        )[0]
                        chat.vacancy = dialog.vacancy
                        mess = (
                            dialog.get_name_last_dialog()
                            + "\n\n"
                            + str(_("Your can send a message to the HR."))
                        )
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=mess),
                                viber_keyboard(chat=chat, dialogs=dialogs),
                            ],
                        )
                    except:
                        chat.status = Chat.SEARCH
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Enter vacancy for search."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                elif message.text == "closedialog":
                    dialog = ViberDialog.objects.filter(
                        chat=chat, vacancy=chat.vacancy
                    ).first()
                    if dialog:
                        dialog.block = ViberDialog.JS
                        dialog.block_stamp = datetime.now()
                        dialog.save()
                        user = chat.vacancy.user
                        if user and user.viber_id:
                            mes = (
                                _("Applicant ")
                                + chat.name
                                + _(" withdrew. Vacancy:")
                                + chat.vacancy.vacancy
                            )
                            viber_bot.send_messages(
                                user.viber_id,
                                [
                                    TextMessage(text=str(mes)),
                                    viber_keyboard(chat=chat, user=user),
                                ],
                            )
                        ViberResponseDialog(dialog=dialog).delete()
                        ViberDialog.objects.filter(
                            chat=chat, vacancy=chat.vacancy
                        ).delete()
                        chat.status = Chat.SEARCH
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Enter vacancy for search."))),
                                viber_keyboard(chat=chat, dialogs=dialogs),
                            ],
                        )
                    else:
                        chat.status = Chat.SELECTION
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(
                                    text=str(
                                        _(
                                            "Select the vacancy for which the closing dialogue."
                                        )
                                    )
                                ),
                                viber_keyboard(chat=chat, dialogs=dialogs),
                            ],
                        )
                elif message.text == "previousstep":
                    dialog = ViberDialog.objects.filter(
                        chat=chat, vacancy=chat.vacancy
                    ).first()
                    if (
                        dialog
                        and chat.previous_status
                        and chat.previous_status == Chat.ANSWER
                    ):
                        chat.status = Chat.ANSWER
                        chat.save()
                        response_dialog = ViberResponseDialog(
                            dialog=dialog, text=message.text, question=False
                        )
                        response_dialog.save()
                        questions = dialog.dialog.split("~")
                        if dialog.step and dialog.step < len(questions):
                            mess = questions[dialog.step]
                            dialog.step += 1
                            dialog.save()
                            viber_bot.send_messages(
                                viber_request.sender.id,
                                [TextMessage(text=mess), viber_keyboard(chat=chat)],
                            )
                        elif dialog.step and dialog.step == len(questions):
                            dialog.step.dialog = None
                            dialog.step.step = None
                            viber_bot.send_messages(
                                viber_request.sender.id,
                                [
                                    TextMessage(text=str(_("Ask a HR a question."))),
                                    viber_keyboard(chat=chat),
                                ],
                            )
                        else:
                            dialog.step.dialog = None
                            dialog.step.step = None
                            chat.status = Chat.SEARCH
                            chat.save()
                            viber_bot.send_messages(
                                viber_request.sender.id,
                                [
                                    TextMessage(
                                        text=str(_("Enter vacancy for search."))
                                    ),
                                    viber_keyboard(chat=chat),
                                ],
                            )
                        dialog.step.save()
                    if (
                        dialog
                        and chat.previous_status
                        and chat.previous_status == Chat.RESPONSE
                    ):
                        chat.status = Chat.RESPONSE
                        chat.vacancy = chat.previous_vacancy
                        mess = (
                            dialog.get_name_last_dialog(messages=2)
                            + "\n\n"
                            + str(_("Your can send a message to the HR."))
                        )
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat)],
                        )
                    else:
                        chat.status = Chat.SEARCH
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Enter vacancy for search."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                elif message.text == "search":
                    chat.status = Chat.SEARCH
                    chat.save()
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [
                            TextMessage(text=str(_("Enter vacancy for search."))),
                            viber_keyboard(chat=chat),
                        ],
                    )
                else:
                    user = chat.vacancy.user
                    if user and user.viber_id:
                        viber_bot.send_messages(
                            user.viber_id,
                            [
                                TextMessage(
                                    text=str(
                                        _("Your have a new message from jobseeker.")
                                    )
                                ),
                                viber_keyboard(chat=chat, user=user),
                            ],
                        )
                        dialog = ViberDialog.objects.filter(
                            chat=chat, vacancy=chat.vacancy
                        ).first()
                        if dialog:
                            response_dialog = ViberResponseDialog(
                                dialog=dialog, text=message.text, question=False
                            )
                            response_dialog.save()
                        else:
                            dialog = ViberDialog(
                                chat=chat,
                                vacancy=chat.vacancy,
                                text=message.text,
                                question=False,
                            )
                            dialog.save()
                        (
                            response_fo_vacancy,
                            created,
                        ) = ResponseForVacancy.objects.get_or_create(
                            user=user, vacancy=chat.vacancy
                        )
                        response_fo_vacancy.dialog = dialog
                        response_fo_vacancy.message = message.text
                        response_fo_vacancy.views = False
                        response_fo_vacancy.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Message sent to HR."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                    else:
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("HR not found."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
                    ViberDialog.objects.filter(chat=chat, vacancy=chat.vacancy).delete()

            # --------------------------------------------------------------------------------- SELECTION
            elif chat.status == Chat.SELECTION:
                if message.text[:8] == "vacancy-":
                    try:
                        vacancy = Vacancy.objects.get(pk=message.text[8:])
                        chat.status = Chat.RESPONSE
                        chat.vacancy = vacancy
                        dialog = ViberDialog.objects.filter(chat=chat, vacancy=vacancy)[
                            0
                        ]
                        mess = (
                            dialog.get_name_last_dialog(messages=2)
                            + "\n\n"
                            + str(_("Your can send a message to the HR."))
                        )
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat)],
                        )
                    except:
                        chat.status = Chat.SEARCH
                        chat.save()
                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [
                                TextMessage(text=str(_("Enter vacancy for search."))),
                                viber_keyboard(chat=chat),
                            ],
                        )
            # --------------------------------------------------------------------------------- EMPLOEYR START
            elif chat.status == Chat.EMPLOYER_START:
                if chat.hr:

                    crm_id = chat.hr
                    company = Company.objects.filter(crm_client_id=crm_id).first()

                    if company:
                        user.company = company
                    user.role = JobBoardUser.EMPLOYER
                    user.save()

                    chat.status = Chat.EMPLOYER_MENU
                    chat.save()

                    if not company:

                        comp = Company()
                        comp.crm_client_id = crm_id
                        comp.name = "---company---" + str(crm_id)
                        # comp.name_ru = "---company---" + str(crm_id)
                        comp.description = "Компания создана автоматически при регистрации клиента."
                        # comp.description_ru = "Компания создана автоматически при регистрации клиента."
                        comp.visible = False
                        comp.save()

                        mes = "\n\n" + "На сайте создана компания в которой Вы можете создавать вакансии." + "\n" \
                              + "Сейчас компания скрыта. Вакансии будут отображаться без указания компании." + "\n" \
                              + "Вы можете настроить название и описание компании, а также вулючить/отключить отображение комапнии."

                        keyboard = viber_keyboard(chat=chat, company=comp)
                    else:
                        mes = "\n\n" + "Ваша компания зарегистрирована на сайте с названием" + company.name + "\n" \
                              + "Вы можете настроить название и описание компании, а также вулючить/отключить отображение комапнии."

                        for v in Vacancy.objects.filter(company=company):
                            v.user = user
                            v.save()

                        keyboard = viber_keyboard(chat=chat, company=company)

                    for empl in JobBoardUser.objects.filter(viber_id=viber_request.sender.id).exclude(pk=user.id):
                        empl.viber_id = None
                        empl.save()

                    viber_bot.send_messages(viber_request.sender.id, [TextMessage(text=mes), keyboard])

                    # except:
                    #     employer_menu(chat, company=company)
                else:
                    employer_menu(chat, company=None)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR MENU
            elif chat.status == Chat.EMPLOYER_MENU:

                if message.text == "company":
                    company = None
                    try:
                        company = user.company

                        chat.status = Chat.EMPLOYER_COMPANY_MENU
                        chat.save()

                        mess = (
                                "О Вашей компании на сайте присутствкет слндующая информация:"
                                + "\n"
                                + "Наименование:"
                                + company.name
                                + "\n"
                                + "Описание:"
                                + "\n"
                                + company.description
                        )

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )

                    except:
                        employer_menu(chat, company=company)

                elif message.text == "vacancies":
                    try:
                        company = user.company
                        vacancies = Vacancy.objects.filter(company=company, deleted=False)
                        if vacancies:
                            mess = "Ваши вакансии:\n"
                            for vacancy in vacancies:
                                mess += vacancy.vacancy + ' '
                                if vacancy.published:
                                    mess += '--АКТИВНА--\n'
                                else:
                                    mess += '--СКРЫТА--\n'
                        else:
                            mess = "У Вас нет вакансий."
                        chat.status = Chat.EMPLOYER_VACANCY_MENU
                        chat.save()

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    except:
                        employer_menu(chat, company=company)
                else:
                    employer_menu(chat, company=None)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR COMPANY MENU
            elif chat.status == Chat.EMPLOYER_COMPANY_MENU:
                company = None
                try:
                    company = user.company
                    if message.text == "company_change":
                        company = user.company

                        chat.status = Chat.EMPLOYER_COMPANY_NAME
                        chat.save()

                        mess = (
                                "Какое название Вашей компании использовать на сайте?"
                        )

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    if message.text == "company_activate":
                        company = user.company
                        if company.visible:
                            company.visible = False
                            mess = (
                                    "Название Вашей компании скрыто."
                            )
                        else:
                            company.visible = True
                            mess = (
                                    "Название Вашей компании будет отображаться на сайте."
                            )
                        company.save()

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    elif message.text == "emploer_menu":
                        employer_menu(chat, company=company)
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR COMPANY NAME
            elif chat.status == Chat.EMPLOYER_COMPANY_NAME:
                company_name = message.text[:64]
                try:
                    company = user.company
                    if company:
                        company.name = company_name
                        company.visible = True
                        company.save()
                        chat.status = Chat.EMPLOYER_COMPANY_DESCRIPTION
                        chat.save()
                        mess = (
                            "Введите краткое описание Вашей компании:"
                        )
                    else:
                        chat.status = Chat.EMPLOYER_MENU
                        chat.save()
                        mess = (
                            "Компания не найдена. Обратитесь в службу поддержки сайта."
                        )
                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                    )
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR COMPANY DESCRIPTION
            elif chat.status == Chat.EMPLOYER_COMPANY_DESCRIPTION:
                company_description = message.text
                try:
                    company = user.company
                    if company:
                        company.description = company_description
                        company.save()

                        mess = (
                            "ИНФОРМАЦИЯ О ВАШЕЙ КОМПАНИИ НА САЙТЕ ЗАМЕНИНА"
                            + "\n"
                            + "Спасибо."
                        )
                    else:
                        mess = (
                            "Компания не найдена. Обратитесь в службу поддержки сайта."
                        )

                    chat.status = Chat.EMPLOYER_MENU
                    chat.save()

                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                    )
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR COMPANY ACTIVATE
            elif chat.status == Chat.EMPLOYER_COMPANY_ACTIVATE:
                try:
                    company = user.company
                    if company:
                        if company.visible:
                            company.visible = False
                            company.save()
                            mess = "Информация о Вашей компании скрыта на сайте"
                        else:
                            company.visible = True
                            company.save()
                            mess = "Информация о Вашей компании доступна на сайте"
                    else:
                        mess =  "Компания не найдена. Обратитесь в службу поддержки сайта."
                    chat.status = Chat.EMPLOYER_MENU
                    chat.save()

                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                    )
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY MENU
            elif chat.status == Chat.EMPLOYER_VACANCY_MENU:
                company = None
                try:
                    company = user.company
                    if message.text == "employer_vacancy_add":
                        company = user.company

                        chat.status = Chat.EMPLOYER_VACANCY_NAME
                        chat.vacancy = None
                        chat.save()

                        mess = (
                                "Введите название вакансии:"
                        )

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    elif message.text == "employer_vacancy_change":
                        company = user.company

                        chat.status = Chat.EMPLOYER_VACANCY_CHANGE
                        chat.save()

                        mess = (
                                "Выберите вакансию, которую хотите изменить."
                        )

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    elif message.text == "employer_vacancy_start":
                        company = user.company

                        chat.status = Chat.EMPLOYER_VACANCY_START
                        chat.save()

                        mess = (
                                "Выберите вакансию, которую хотите запустить/остановить."
                        )

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    elif message.text == "employer_vacancy_delete":
                        company = user.company

                        chat.status = Chat.EMPLOYER_VACANCY_DELETE
                        chat.save()

                        mess = (
                                "Выберите вакансию, которую хотите УДАЛИТЬ."
                        )

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    elif message.text == "emploer_menu":
                        employer_menu(chat, company=company)
                    else:
                        employer_menu(chat, company=company)
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY NAME
            elif chat.status == Chat.EMPLOYER_VACANCY_NAME:

                vacancy_name = message.text
                company = None
                try:
                    company = user.company
                    # vacancy = Vacancy.objects.filter(vacancy=vacancy_name, company=company, deleted=False)
                    # if vacancy:
                    #     vac = vacancy[0]
                    vac = chat.vacancy
                    if not vac:
                        vac = Vacancy()

                    vac.published_until = timezone.now() + timedelta(days=7)
                    vac.infid_until = timezone.now() + timedelta(days=7)
                    vac.vacancy = vacancy_name
                    vac.vacancy_ru = vacancy_name
                    vac.company = company
                    vac.user = user
                    vac.repeats = 2
                    vac.from_paper = False
                    vac.modified = timezone.now()
                    vac.imported = timezone.now()
                    vac.crm_client_id = company.crm_client_id
                    vac.published = False
                    vac.social_repost = False
                    vac.save()

                    chat.status = Chat.EMPLOYER_VACANCY_DESCRIPTION
                    chat.vacancy = vac
                    chat.save()

                    mess = "Введите описание вакансии"
                    mess += "Номера телефонов набтрайте в формате (000)000-00-00"

                    viber_bot.send_messages(
                        viber_request.sender.id,
                        [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                    )
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY DESCRIPTION
            elif chat.status == Chat.EMPLOYER_VACANCY_DESCRIPTION:
                vacancy_description = message.text
                company = None
                try:
                    company = user.company
                    vac = chat.vacancy
                    if vac:
                        phones = re.findall('(?:\+38|38|8)?(?:(?:\(\d{3}\))?(?:\d{3}))(?:[- ]\d{2,4}){1,2}',
                                            message.text)
                        phones = ','.join(phones)
                        vac.phones = normalize_phones(phones)
                        vac.description = vacancy_description
                        vac.save()

                        chat.status = Chat.EMPLOYER_VACANCY_CATEGORY
                        chat.vacancy = vac
                        chat.save()

                        mess = "Выберите категорию вакансии:"

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )

                    else:
                        employer_menu(chat, company=company)
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY CATEGORY
            elif chat.status == Chat.EMPLOYER_VACANCY_CATEGORY:
                company = None
                # try:

                print('\n\n')
                print('EMPLOYER_VACANCY_CATEGORY')
                print('\n\n')

                company = user.company
                vac = chat.vacancy
                if vac and message.text[:9] == "category-":

                    category = Category.objects.filter(pk=message.text[9:])
                    if category:
                        category = category[0]

                        vac.category = category
                        vac.published = True
                        vac.save()

                        chat.status = Chat.EMPLOYER_MENU
                        chat.vacancy = None
                        chat.save()

                        mess = "Вот и все) Вакансия создана!"

                        viber_bot.send_messages(
                            viber_request.sender.id,
                            [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                        )
                    else:
                        employer_menu(chat, company=company)
                else:
                    employer_menu(chat, company=company)
                # except:
                #     employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY CHANGE
            elif chat.status == Chat.EMPLOYER_VACANCY_CHANGE:
                company = None
                try:
                    company = user.company
                    if message.text[:15] == "vacancy_change-":

                        vac = Vacancy.objects.filter(pk=message.text[15:])
                        if vac:
                            vac = vac[0]

                            chat.status = Chat.EMPLOYER_VACANCY_NAME
                            chat.vacancy = vac
                            chat.save()

                            mess = "Вакансия: " + vac.vacancy + '\n'
                            mess += "Введите новое название вакансии:"

                            viber_bot.send_messages(
                                viber_request.sender.id,
                                [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                            )
                        else:
                            employer_menu(chat, company=company)
                    else:
                        employer_menu(chat, company=company)
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY START
            elif chat.status == Chat.EMPLOYER_VACANCY_START:
                company = None
                try:
                    company = user.company
                    if message.text[:14] == "vacancy_start-":

                        vac = Vacancy.objects.filter(pk=message.text[14:])
                        if vac:
                            vac = vac[0]
                            if vac.published:
                                vac.published = False
                                mess = "Вакансия остановлена."
                            else:
                                vac.published = True
                                mess = "Вакансия запущена."
                            vac.save()

                            chat.status = Chat.EMPLOYER_MENU
                            chat.vacancy = None
                            chat.save()

                            viber_bot.send_messages(
                                viber_request.sender.id,
                                [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                            )
                        else:
                            employer_menu(chat, company=company)
                    else:
                        employer_menu(chat, company=company)
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)
            # --------------------------------------------------------------------------------- EMPLOEYR VACANCY DELETE
            elif chat.status == Chat.EMPLOYER_VACANCY_DELETE:
                company = None
                try:
                    company = user.company
                    if message.text[:15] == "vacancy_delete-":

                        vac = Vacancy.objects.filter(pk=message.text[15:])
                        if vac:
                            vac = vac[0]
                            vac.published = False
                            vac.deleted = True
                            vac.save()

                            mess = "Вакансия удалена."

                            chat.status = Chat.EMPLOYER_MENU
                            chat.vacancy = None
                            chat.save()

                            viber_bot.send_messages(
                                viber_request.sender.id,
                                [TextMessage(text=mess), viber_keyboard(chat=chat, company=company)],
                            )
                        else:
                            employer_menu(chat, company=company)
                    else:
                        employer_menu(chat, company=company)
                except:
                    employer_menu(chat, company=company)
                return HttpResponse(status=200)

            # ------------------------------------------------------------------------------------------------------
            else:
                chat.status = Chat.SEARCH
                chat.save()
                viber_bot.send_messages(
                    viber_request.sender.id,
                    [
                        TextMessage(text=str(_("Enter vacancy for search."))),
                        viber_keyboard(chat=chat),
                    ],
                )
                return HttpResponse(status=200)

        else:
            return HttpResponse(status=200) #ViberDeliveredRequest, ViberSeenRequest
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)

def employer_menu(chat, company=None):
    chat.status = Chat.EMPLOYER_MENU
    chat.save()
    viber_bot.send_messages(
        chat.chat_id,
        [
            TextMessage(text=EMPLOYRE_GREETINGS),
            viber_keyboard(chat=chat, company=company),
        ],
    )
