from django.db import models
from django.conf import settings


class Recipients(models.Model):
    chat_id = models.CharField(max_length=70, default="")
    login_name = models.CharField(max_length=70, default="")
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    phone_number = models.CharField(max_length=20, default="")
    address = models.CharField(max_length=300, default="")
    email = models.EmailField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    disabilities = models.BooleanField(default=False)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Recipients"
        verbose_name_plural = "Recipients"


class Relatives(models.Model):
    recipient = models.ForeignKey(Recipients, blank=True, null=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    disabilities = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Relatives"
        verbose_name_plural = "Relatives"


class Address(models.Model):
    recipient = models.ForeignKey(Recipients, blank=True, related_name="+", null=True, on_delete=models.DO_NOTHING)
    region = models.CharField(max_length=70, default="")
    city = models.CharField(max_length=70, default="")
    street = models.CharField(max_length=100, default="")
    building = models.IntegerField(blank=True, null=True)
    apartment = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Address"


class Categories(models.Model):
    name = models.CharField(max_length=70, default="")
    index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Categories"
        verbose_name_plural = "Categories"


class Subcategories(models.Model):
    name = models.CharField(max_length=70, default="")
    category = models.ForeignKey(Categories, blank=True, null=True, on_delete=models.CASCADE)
    index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Subcategories"
        verbose_name_plural = "Subcategories"


class Volunteers(models.Model):
    login_name = models.CharField(max_length=30, default="")
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    phone_number = models.CharField(max_length=70, default="")
    email = models.EmailField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Volunteers"
        verbose_name_plural = "Volunteers"


class Requests(models.Model):
    category = models.ForeignKey(Categories, blank=True, null=True, on_delete=models.DO_NOTHING)
    subcategory = models.ForeignKey(Subcategories, blank=True, null=True, on_delete=models.DO_NOTHING)
    recipient = models.ForeignKey(Recipients, blank=True, null=True, on_delete=models.DO_NOTHING)
    volunteer = models.ForeignKey(Volunteers, blank=True, null=True, on_delete=models.DO_NOTHING)
    priority = models.CharField(max_length=70, default="")      #   high / normal / low
    added = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=2000, default="")
    photo = models.ImageField(upload_to="requests_images/", blank=True)
    regular = models.BooleanField(default=False)
    status = models.CharField(max_length=70, default="")        #   created / approved / gathered / done / declined

    class Meta:
        verbose_name = "Requests"
        verbose_name_plural = "Requests"


class Feedbacks(models.Model):
    request = models.ForeignKey(Requests, blank=True, null=True, on_delete=models.DO_NOTHING)
    recipient = models.ForeignKey(Recipients, blank=True, null=True, on_delete=models.DO_NOTHING)
    volunteer = models.ForeignKey(Volunteers, blank=True, null=True, on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=2000, default="")
    photo = models.ImageField(upload_to="feedback_images/", blank=True)
    range = models.CharField(max_length=70, default="")

    class Meta:
        verbose_name = "Feedbacks"
        verbose_name_plural = "Feedbacks"


class Messages(models.Model):
    welcome_message = models.TextField(default="")
    call_for_registration_message = models.TextField(default="")
    choice_message = models.TextField(default="")
    deletion_message = models.TextField(default="")
    call_for_phone_message = models.TextField(default="")
    call_for_name_surname_message = models.TextField(default="")
    call_for_bday_message = models.TextField(default="")
    call_for_address_message = models.TextField(default="")
    call_for_email_message = models.TextField(default="")
    successful_registration_message = models.TextField(default="")
    select_category_message = models.TextField(default="")
    request_help_comment_message = models.TextField(default="")
    save_request_message = models.TextField(default="")
    request_status_notification_message = models.TextField(default="")
    receiving_help_comment_message = models.TextField(default="")

    class Meta:
        verbose_name = "Messages"
        verbose_name_plural = "Messages"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if Messages.objects.count() != 1:
            self.delete()


class Chat(models.Model):

    WELCOME_MESSAGE = 1
    REGISTRATION_START = 2
    SETTING_PHONE = 3
    SETTING_NAME_SURNAME = 4
    SETTING_DATE_OF_BRTH = 5
    SETTING_ADRESS = 6
    SETTING_EMAIL = 7
    REGISTRATION_COMPLETE = 8
    CHOICE_MESSAGE = 9
    LIST_OF_REQUESTS = 10
    REQUEST_WAS_DELETED = 11
    SELECT_CATEGORY = 12
    FOOD_CATEGORIES = 13
    REPAIR_BUDGET = 14
    LEAVE_REPAIR_PHOTO = 15
    REQUEST_COMMENT_MESSAGE = 16
    REQUEST_SAVED = 17
    SEND_REQUEST_STATUS_MESSAGE = 18
    SEND_HELP_RECEIVED_MESSAGE = 19

    STATUS = (
        (REGISTRATION_START, "Starting registration"),
        (SETTING_PHONE, "Print your phone"),
        (SETTING_NAME_SURNAME, "Print your firstname and surname"),
        (SETTING_DATE_OF_BRTH, "Print your date of birthday"),
        (SETTING_EMAIL, "Print your email, if you have"),
        (REGISTRATION_COMPLETE, "Registration is complete"),
        (CHOICE_MESSAGE, "Need help or my requests"),
        (LIST_OF_REQUESTS, "List of requests"),
        (REQUEST_WAS_DELETED, "Request was deleted"),
        (WELCOME_MESSAGE, "Welcome message"),
        (SELECT_CATEGORY, "Select category"),
        (FOOD_CATEGORIES, "Food categories"),
        (REPAIR_BUDGET, "Print repair budget"),
        (LEAVE_REPAIR_PHOTO, "Upload photo"),
        (REQUEST_COMMENT_MESSAGE, "Print your comment"),
        (REQUEST_SAVED, "Request is saved "),
        (SEND_REQUEST_STATUS_MESSAGE, "Send request status massage"),
        (SEND_HELP_RECEIVED_MESSAGE, "Send help request message"),
    )

    chat_id = models.CharField(max_length=64, db_index=True)
    status = models.PositiveIntegerField("chat status", choices=STATUS, default=WELCOME_MESSAGE)
    recipient = models.ForeignKey(Recipients, blank=True, null=True, on_delete=models.SET_NULL)
    volunteer = models.ForeignKey(Volunteers, blank=True, null=True, on_delete=models.SET_NULL)
    open_request = models.ForeignKey(Requests, default=None, blank=True, null=True, on_delete=models.SET_NULL)