from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('', views.settings, name='settings.html'),
    path('update_Brightness/', views.update_Brightness, name='update_Brightness'),
]