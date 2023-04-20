from django.contrib import admin
from django.contrib.auth.models import Group
from bot.models import Recipients, Categories, Requests, Volunteers, Feedbacks, Messages


class RecipientsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "surname",
        "phone_number",
        "email",
        "date_of_birth",
        "disabilities",
    )


class CategoriesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )


class RequestsAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "recipient",
        "volunteer",
        "priority",
        "added",
        "comment",
        "photo",
        "regular",
        "status",
    )


class VolunteersAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "surname",
        "phone_number",
        "email",
    )


class FeedbacksAdmin(admin.ModelAdmin):
    list_display = (
        "request",
        "recipient",
        "volunteer",
        "comment",
        "photo",
        "range",
    )


class MessagesAdmin(admin.ModelAdmin):
    list_display = (
        "welcome_message",
        "call_for_registration_message",
        "choice_message",
        "deletion_message",
        "call_for_phone_message",
        "call_for_name_surname_message",
        "call_for_bday_message",
        "call_for_address_message",
        "call_for_email_message",
        "successful_registration_message",
        "select_category_message",
        "request_help_comment_message",
        "save_request_message",
        "request_status_notification_message",
        "receiving_help_comment_message",
    )


admin.site.register(Recipients, RecipientsAdmin)

admin.site.register(Categories, CategoriesAdmin)

admin.site.register(Requests, RequestsAdmin)

admin.site.register(Volunteers, VolunteersAdmin)

admin.site.register(Feedbacks, FeedbacksAdmin)

admin.site.register(Messages, MessagesAdmin)

admin.site.unregister(Group)
