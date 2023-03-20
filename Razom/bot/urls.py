from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = "thepage"

urlpatterns = [
    path("", csrf_exempt(views.BasicBotView.as_view()), name="bot"),
]
