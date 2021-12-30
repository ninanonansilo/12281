from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    first_name = None
    last_name = None
    groups = None
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    setup_place = models.CharField(verbose_name='설치 장소', max_length=50)
    setup_day = models.CharField(verbose_name='설치 날짜', help_text='설치 날짜를 입력하시오, YYYY/MM/DD hh:mm:ss', max_length=19)
    company_name = models.CharField(verbose_name='업체명', help_text='업체명을 입력하시오', max_length=100)
    display = models.CharField(verbose_name='해상도', max_length=9, help_text='해상도를 입력하시오, NxM')
    max_brgt = models.IntegerField(verbose_name='최대 밝기', default=0)
    player_serial = models.CharField(verbose_name='플레이어 Serial', unique=True, primary_key=True, max_length=16)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    login_fail_count = models.IntegerField(default=0)
    login_time = models.CharField(help_text='hh:mm:ss', max_length=50,default=0)



    var_user_id = models.CharField(verbose_name='user_id', max_length=50)
    var_picture_index = models.IntegerField(verbose_name='picture_index', default=-1)
    var_text_index= models.IntegerField(verbose_name='text_index', default=-1, blank=True, null=False)
    var_check_index = models.IntegerField(verbose_name='check_index', default=2)
    var_move_movie_index = models.IntegerField(verbose_name='move_movie_index', default=-1)
    var_sun = models.IntegerField(verbose_name='sun', default=-1)
    var_mon = models.IntegerField(verbose_name='mon', default=-1)
    var_tues = models.IntegerField(verbose_name='tues', default=-1)
    var_wed = models.IntegerField(verbose_name='wed', default=-1)
    var_thurs = models.IntegerField(verbose_name='thurs', default=-1)
    var_fri = models.IntegerField(verbose_name='fri', default=-1)
    var_sat = models.IntegerField(verbose_name='sat', default=-1)
    var_pattern_now = models.IntegerField(verbose_name='pattern_now', default=-1)
    var_my = models.IntegerField(verbose_name='my', default=2)
    var_bright_check = models.IntegerField(verbose_name='bright_check', default=36)
    var_CDS_check = models.IntegerField(verbose_name='CDS_check', default=0)
    var_auto_bright_max_check = models.IntegerField(verbose_name='auto_bright_max_check', default=-1)
    var_auto_bright_min_check = models.IntegerField(verbose_name='auto_bright_min_check', default=-1)
    var_auto_CDS_max_check = models.IntegerField(verbose_name='auto_CDS_max_check', default=-1)
    var_auto_CDS_min_check = models.IntegerField(verbose_name='auto_CDS_min_check', default=-1)
    var_auto_on_hour_check = models.IntegerField(verbose_name='auto_on_hour_check', default=-1)
    var_auto_on_min_check = models.IntegerField(verbose_name='auto_on_min_check', default=-1)
    var_auto_off_hour_check = models.IntegerField(verbose_name='auto_off_hour_check', default=-1)
    var_auto_off_min_check = models.IntegerField(verbose_name='auto_off_min_check', default=-1)
    var_first_loading = models.IntegerField(verbose_name='first_loading', default=1)
    var_brightness_mode = models.IntegerField(verbose_name='brightness_mode', default=-1)
    var_powermode = models.IntegerField(verbose_name='powermode', default=-1)
    var_manualcontrol = models.IntegerField(verbose_name='manualcontrol', default=-1)
