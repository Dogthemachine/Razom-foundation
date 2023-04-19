from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = "bot"

urlpatterns = [
    path("", views.BasicBotView, name="bot"),
]
