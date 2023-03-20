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


class Relatives(models.Model):
    recipient = models.ForeignKey(Recipients, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    disabilities = disabilities = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)


class Address(models.Model):
    recipient = models.ForeignKey(Recipients, on_delete=models.CASCADE)
    region = models.CharField(max_length=70, default="")
    city = models.CharField(max_length=70, default="")
    street = models.CharField(max_length=100, default="")
    building = models.IntegerField(blank=True, null=True)
    apartment = models.IntegerField(blank=True, null=True)


class Requests(models.Model):
    category = ForeignKey(Categories, on_delete=models.CASCADE)
    priority = models.CharField(max_length=70, default="")      #   high / normal / low
    added = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=2000, default="")
    photo = models.ImageField(upload_to="requests_images/", blank=True)
    regular = models.BooleanField(default=False)
    status = models.CharField(max_length=70, default="")        #   created / approved / gathered / done / declined


class Feedbacks(models.Model):
    request = ForeignKey(Requests, on_delete=models.CASCADE)
    volunteer = ForeignKey(Volunteers, on_delete=models.CASCADE)
    comment = models.CharField(max_length=2000, default="")
    photo = models.ImageField(upload_to="feedback_images/", blank=True)
    range = models.CharField(max_length=70, default="")


class Volunteers(models.Model):
    login_name = models.CharField(max_length=30, default="")
    name = models.CharField(max_length=30, default="")
    surname = models.CharField(max_length=30, default="")
    phone_number = models.CharField(max_length=70, default="")
    email = models.EmailField(max_length=200, null=True, blank=True)


class Categories(models.Model):
    name = models.CharField(max_length=70, default="")
