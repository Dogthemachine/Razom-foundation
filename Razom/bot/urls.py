from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

print("\n\n", "START URLS", "\n\n")

app_name = "bot"

urlpatterns = [
    path("", views.BasicBotView, name="bot"),
]
