from django.db import models
from django.conf import settings


class Recipients(models.Model):
    chat_id = models.CharField(max_length=70, default="")
    login_name = models.CharField(max_length=70, default="")
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    phone_number = models.CharField(max_length=20, default="")
    email = models.EmailField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    disabilities = models.BooleanField(default=False)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Recipients"
        verbose_name_plural = "Recipients"


class Relatives(models.Model):
    recipient = models.ForeignKey(Recipients, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    disabilities = disabilities = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Relatives"
        verbose_name_plural = "Relatives"


class Address(models.Model):
    recipient = models.ForeignKey(Recipients, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    region = models.CharField(max_length=70, default="")
    city = models.CharField(max_length=70, default="")
    street = models.CharField(max_length=100, default="")
    building = models.IntegerField(blank=True, null=True)
    apartment = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Address"


class Categories(models.Model):
    name = models.CharField(max_length=70, default="")

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Categories"
        verbose_name_plural = "Categories"


class Volunteers(models.Model):
    login_name = models.CharField(max_length=30, default="")
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    phone_number = models.CharField(max_length=70, default="")
    email = models.EmailField(max_length=200, null=True, blank=True)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Volunteers"
        verbose_name_plural = "Volunteers"


class Requests(models.Model):
    category = models.ForeignKey(Categories, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    recipient = models.ForeignKey(Recipients, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    volunteer = models.ForeignKey(Volunteers, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    priority = models.CharField(max_length=70, default="")      #   high / normal / low
    added = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=2000, default="")
    photo = models.ImageField(upload_to="requests_images/", blank=True)
    regular = models.BooleanField(default=False)
    status = models.CharField(max_length=70, default="")        #   created / approved / gathered / done / declined

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Requests"
        verbose_name_plural = "Requests"


class Feedbacks(models.Model):
    request = models.ForeignKey(Requests, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    recipient = models.ForeignKey(Recipients, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    volunteer = models.ForeignKey(Volunteers, blank=True, null=True, related_name="+", on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=2000, default="")
    photo = models.ImageField(upload_to="feedback_images/", blank=True)
    range = models.CharField(max_length=70, default="")

    def __str__(self):
        return u"%s" % self.name

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

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Messages"
        verbose_name_plural = "Messages"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if Messages.objects.count() != 1:
            self.delete()

