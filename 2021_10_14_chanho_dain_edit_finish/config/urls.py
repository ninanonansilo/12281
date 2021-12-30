"""Actvision URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home0
    .
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import loginapp.views
import home.views
import movie.views
import settings.views
import inform.views
import register.views
import imgn.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginapp.views.login, name='login.html'),
    path('logout', loginapp.views.logout, name='logout'),
    path('login/', loginapp.views.login_success, name='login_success.html'),
    path('home', loginapp.views.home, name='home.html'),
    path('home/movie', movie.views.movie, name='movie.html'),
    path('home/movie/upmove_movie', movie.views.upmove_movie, name='upmove_movie'),
    path('home/movie/downmove_movie', movie.views.downmove_movie, name='downmove_movie'),
    path('home/movie/video_list', movie.views.video_list, name='video_list'),
    path('home/movie/upload_list', movie.views.upload_list, name='upload_list'),
    path('home/movie/upload_video', movie.views.upload_video, name='upload_video'),
    path('home/movie/delete_play_list', movie.views.delete_play_list, name='delete_play_list'),
    path('home/movie/delete_video', movie.views.delete_video, name='delete_video'),
    path('home/movie/play_schedule', movie.views.play_schedule, name='play_schedule'),
    path('home/movie/play_list_trans', movie.views.play_list_trans, name='play_list_trans'),
    # path('home/setting', include('settings.urls')),
    path('home/setting', settings.views.settings, name='settings.html'),
    path('home/setting/check_pattern', settings.views.check_pattern, name='check_pattern'),
    path('home/setting/check_Brightness_mode', settings.views.check_Brightness_mode, name='check_Brightness_mode'),
    path('home/setting/update_Brightness', settings.views.update_Brightness, name='update_Brightness'),
    path('home/setting/update_CDS_Value', settings.views.update_CDS_Value, name='update_CDS_Value'),
    path('home/setting/update_min_max', settings.views.update_min_max, name='update_min_max'),
    path('home/setting/power_mode', settings.views.power_mode, name='power_mode'),
    path('home/setting/manual_control', settings.views.manual_control, name='manual_control'),
    path('home/setting/update_on_off', settings.views.update_on_off, name='update_on_off'),
    path('home/inform', inform.views.inform, name='inform.html'),
    path('home/register', register.views.register, name='register.html'),
    path('home/register/users_list', register.views.users_list, name='users_list'),
    path('home/imgn', imgn.views.imgn, name='image.html'),
    path('home/imgn/upload_img', imgn.views.upload_img, name='upload_img'),
    path('home/imgn/save_letter', imgn.views.save_letter, name='save_letter'),
    path('home/imgn/event_trans', imgn.views.event_trans, name='event_trans'),
    path('home/imgn/save_img', imgn.views.save_img, name='save_img'),
    path('home/imgn/delete_img', imgn.views.delete_img, name='delete_img'),
    path('home/imgn/delete_text', imgn.views.delete_text, name='delete_text'),
    path('home/imgn/make_text_preview', imgn.views.make_text_preview, name='make_text_preview'),
    path('home/imgn/edit_letter', imgn.views.edit_letter, name='edit_letter'),
    path('home/imgn/session_text_json', imgn.views.session_text_json, name='session_text_json'),
    path('home/imgn/downmove_picture', imgn.views.downmove_picture, name='downmove_picture'),
    path('home/imgn/upmove_picture', imgn.views.upmove_picture, name='upmove_picture'),
    path('home/imgn/downmove_letter', imgn.views.downmove_letter, name='downmove_letter'),
    path('home/imgn/upmove_letter', imgn.views.upmove_letter, name='upmove_letter'),
    path('home/register/input', register.views.signup, name='signup'),
]
