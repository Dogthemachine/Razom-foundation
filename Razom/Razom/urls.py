from django.contrib import admin
from django.urls import include, path


urlpatterns = []

urlpatterns += (
    path("", include("bot.urls")),
    path("admin/", admin.site.urls),
)
