from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = "bot"

urlpatterns = [
    # path("", csrf_exempt(views.BasicBotView.as_view()), name="bot"),
    path("", views.telegram_webhook, name="webhook"),
]
