from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("register/", admin.site.urls),
]
