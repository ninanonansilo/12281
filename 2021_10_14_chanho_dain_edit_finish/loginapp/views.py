from logging import info
from django.core import paginator
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from django import forms
from register.models import Profile
from settings.update_json import *
from django.db import IntegrityError
import sqlite3
from django.contrib import messages
from django.contrib.auth.hashers import check_password
import datetime


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']  # 로그인 시에는 유저이름과 비밀번호만 입력 받는다.


# Create your views here.
def login(request):
    get_root_json_from_GCP()
    add_database()
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('login.html')


def login_success(request):
    # get_root_json_from_GCP()
    # add_database()
    error = " "
    error_content_plus = ""
    remain_time = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if ((username == '')):  # ID: 미입력,
            # messages.warning(request, "ID를 입력해 주세요")
            error_title = "ID 입력"
            error_content = "ID를 입력해 주세요"
            error = "error"
            return render(request, 'login.html',
                          {'error_title': error_title, 'error_content': error_content, 'error': error})
        if ((username != '') and (password == '')):  # ID: 입력, PW: 미입력
            error_title = "Password 입력"
            error_content = "Password를 입력해 주세요"
            error = "error"
            # messages.warning(request, "Password를 입력해 주세요")
            return render(request, 'login.html',
                          {'error_title': error_title, 'error_content': error_content, 'error': error})
        if not User.objects.filter(username=request.POST['username']).exists():
            error_title = "ID 확인"
            error_content = "존재하지 않은 ID 입니다"
            error = "error"
            # messages.warning(request, "존재하지 않은 ID 입니다")
            return render(request, 'login.html',
                          {'error_title': error_title, 'error_content': error_content, 'error': error})
        user_id = User.objects.get(username=request.POST["username"])
        if not check_password(password, user_id.password):
            error_title = "Passward 확인"
            error_content = "비밀번호가 일치하지 않습니다"
            error = "error"
            if user_id.profile.login_fail_count >= 5:
                datemfomat = "%Y-%m-%d %H:%M:%S"
                if user_id.profile.login_fail_count == 5:
                    current = time_now()  # 현재시간 받아오기
                    int_current = str(current.strftime(datemfomat))
                    later_time = current + timedelta(seconds=3600)  # 로그인 가능한 시간
                    int_later_time = str(later_time.strftime(datemfomat))
                    user_id.profile.login_time = int_later_time
                    user_id.profile.login_fail_count += 1
                    user_id.profile.save(update_fields=['login_fail_count'])
                    user_id.profile.save(update_fields=['login_time'])
                current = time_now()  # 현재시간 받아오기
                int_current = str(current.strftime(datemfomat))
                int_current = datetime.datetime.strptime(int_current, datemfomat)
                later_time = datetime.datetime.strptime(user_id.profile.login_time, datemfomat)
                remain_time = int((later_time - int_current).seconds / 60)
                if remain_time > 60:
                    user_id.profile.login_fail_count = 0
                    user_id.profile.save(update_fields=['login_fail_count'])
                    remain_time = ""
                else:
                    error_title = "Passward 실패"
                    error_content = "Passward 입력 가능 시간이 "
                    error_content_plus = "분이 남았습니다."


            # 패스워드 불일치 => 로그인 실패
            else:
                user_id.profile.login_fail_count += 1  # 다인추가
                user_id.profile.save(update_fields=['login_fail_count'])  # 다인추가
            # messages.warning(request, "Password가 일치하지 않습니다")
            return render(request, 'login.html',
                          {'error_title': error_title, 'error_content': error_content, 'error': error,
                           'remain_time': remain_time, 'error_content_plus': error_content_plus})
        if user_id.profile.login_fail_count >= 5:
            error_title = "Passward 확인"
            error_content = "비밀번호가 일치하지 않습니다"
            error = "error"
            datemfomat = "%Y-%m-%d %H:%M:%S"
            if user_id.profile.login_fail_count == 5:
                current = time_now()  # 현재시간 받아오기
                int_current = str(current.strftime(datemfomat))
                later_time = current + timedelta(seconds=3600)  # 로그인 가능한 시간
                int_later_time = str(later_time.strftime(datemfomat))
                user_id.profile.login_time = int_later_time
                user_id.profile.login_fail_count += 1
                user_id.profile.save(update_fields=['login_fail_count'])
                user_id.profile.save(update_fields=['login_time'])
            current = time_now()  # 현재시간 받아오기
            int_current = str(current.strftime(datemfomat))
            int_current = datetime.datetime.strptime(int_current, datemfomat)
            later_time = datetime.datetime.strptime(user_id.profile.login_time, datemfomat)
            remain_time = int((later_time - int_current).seconds / 60)
            if remain_time > 60:
                user_id.profile.login_fail_count = 0
                user_id.profile.save(update_fields=['login_fail_count'])
                remain_time = ""
            else:
                error_title = "Passward 실패"
                error_content = "Passward 입력 가능 시간이 "
                error_content_plus = "분이 남았습니다."
            return render(request, 'login.html',
                          {'error_title': error_title, 'error_content': error_content, 'error': error,
                           'remain_time': remain_time, 'error_content_plus': error_content_plus})

        if user is not None:
            auth.login(request, user)
            userinfo = User.objects.get(username=request.user.username)
            profile = Profile()
            user_id.profile.login_fail_count = 0  # 패스워드 실패 횟수를 0으로 초기화
            user_id.profile.save(update_fields=['login_fail_count'])
            print("로그인한 Serial 번호 :")
            print(user.profile.player_serial)
            userinfo.profile.var_user_id = user.profile.player_serial
            logined_id = userinfo.profile.player_serial
            ####################### 최적화 ######################

            ###### 현재 GCP에서 관리하고있는 사용자 LIST  #####
            blobs = storage_client.list_blobs(using_bucket)
            list_blob = []
            for blob in blobs:
                if (len(blob.name) == 17):
                    list_blob.append(blob.name[0:-1])
                else:
                    pass
            print("현재 보유 중 : {}".format(list_blob))
            exist_index = 0

            ##### 로그인 Serial 번호가 기존에 있는지 확인 #####
            if logined_id == 'administrator':
                pass
            else:
                for i in range(len(list_blob)):
                    if (logined_id == list_blob[i]):
                        exist_index = 1  # 있으면 1 (문제 없는 상태)
                        # 타임테이블(마지막 하나 남기고), READALL (2개 빼고), MEDIA/image , MEDIA/video 삭제   -> 파이 측이랑 얽힌 부분이 있어 미사용
                        # delete_timetable_list = []
                        # delete_readall_list = []
                        # blobs2 = storage_client.list_blobs(using_bucket)
                        # except_str1 = str(user_id + "/JSON/TIMETABLE/")  # 제외시킬 문자열
                        # except_str2 = str(user_id + "/MEDIA/video/")  # 제외시킬 문자열
                        # except_str3 = str(user_id + "/MEDIA/image/")  # 제외시킬 문자열
                        # except_str4 = str(user_id + "/JSON/READALL/")  # 제외시킬 문자열
                        # for blob in blobs2:
                        #    if blob.name.startswith(except_str1):
                        #        delete_timetable_list.append(blob.name)
                        #    if blob.name.startswith(except_str2):
                        #        delete_blob(using_bucket, blob.name)
                        #    if blob.name.startswith(except_str3):
                        #        delete_blob(using_bucket, blob.name)
                        #    if blob.name.startswith(except_str4):
                        #        delete_readall_list.append(blob.name)
                        # if (len(delete_timetable_list) > 1): # 타임테이블은 1개 이상일 때 뒤에 하나빼고 다 삭제
                        #    for j in range(len(delete_timetable_list) -1):
                        #        delete_blob(using_bucket, delete_timetable_list[j])
                        # if (len(delete_readall_list) > 2): # READALL은 2개 이상일 때 뒤에 두개 빼고 다 삭제
                        #    for j in range(len(delete_readall_list) - 2):
                        #        delete_blob(using_bucket, delete_readall_list[j])

                    else:  # 기존에 해당하는 디렉토리 파일이 없는 경우우
                        pass

                if (exist_index == 0):  # 로그인한 시리얼 번호가 존재 X (신규 유저거나, 디렉토리가 임의로 삭제당한 경우)
                    UPLOAD(using_bucket, "test", logined_id + "/")  # 디렉토리 생성
                    UPLOAD(using_bucket, "test", logined_id + "/" + "IMAGE/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "JSON/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "JSON/RASPI/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "JSON/READALL/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "JSON/TEXT_LIST/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "JSON/TIMETABLE/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "MEDIA/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "MEDIA/image/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "MEDIA/video/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "PLAY_LIST/")
                    UPLOAD(using_bucket, "test", logined_id + "/" + "VIDEO_SCHEDULE/")
                    UPLOAD(using_bucket, "home/static/default_table",
                           logined_id + "/" + "JSON/TIMETABLE/00000000000000")
                    UPLOAD(using_bucket, "home/static/default_video.mp4",
                           logined_id + "/" + "MEDIA/video/default_video.mp4")
                    init_setting = setting_json()
                    print(init_setting)
                    print(init_setting)
                    print(init_setting)
                    print(user_id)
                    print(user_id)
                    print(user_id)
                    print(logined_id)
                    print(logined_id)
                    print(logined_id)
                    save_file(logined_id, init_setting)
                    UPLOAD(using_bucket, str(logined_id) + "/send",
                           str(logined_id) + "/JSON/READALL" + "/00000000000000")
                    UPLOAD(using_bucket, str(logined_id) + "/send",
                           str(logined_id) + "/JSON/READALL" + "/00000000000001")

                createDirectory(logined_id)

            return render(request, 'home.html', {'userinfo': userinfo, 'profile': profile})
        else:
            return render(request, 'login.html')
    return render(request, 'login.html')


def home(request):
    userinfo = User.objects.get(username=request.user.username)
    profile = Profile()
    return render(request, 'home.html', {'userinfo': userinfo, 'profile': profile})


def get_root_json_from_GCP(bucket_name="211004-act"):  # download the json
    # always raspi serial is 16 string
    os.system("rm -rf " + top_directory + "root/*")  # initailizing the root file,
    blobs = storage_client.list_blobs(bucket_name)
    for i in blobs:
        if (i.name[17:21] == "root"):
            DOWNLOAD(bucket_name, i.name,
                     top_directory + root_directory + i.name[0:16] + "_root.json")  # download with serial + root.json


def add_database():
    json_list = os.listdir(top_directory + root_directory)
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor

    # print(json_list)
    for i in range(len(json_list)):
        json_list[i] = root_directory + json_list[i]
        with open(json_list[i], 'r', encoding="utf-8-sig") as outfile:
            read_json_info = json.load(outfile)
            username = read_json_info["id"]
            password = read_json_info["pw"]
            setup_place = read_json_info['setup_place']
            year = str(read_json_info['setup_day']['year']).zfill(4);
            month = str(read_json_info['setup_day']['month']).zfill(2)
            day = str(read_json_info['setup_day']['day']).zfill(2);
            hour = str(read_json_info['setup_day']['hour']).zfill(2)
            minute = str(read_json_info['setup_day']['minute']).zfill(2);
            second = str(read_json_info['setup_day']['second']).zfill(2)
            setup_day = year + '/' + month + '/' + day + ' ' + hour + ':' + minute + ':' + second;
            display = str(read_json_info['display']['width']) + 'x' + str(read_json_info['display']['height']);
            max_brgt = str(read_json_info['max_brightness']);
            player_serial = str(read_json_info['serial']);
            company_name = str(read_json_info['company_name']);
            # UserInfo = User(username, password)
            UserInfo = User()
            UserProfile = Profile()
            UserInfo.username = username
            UserInfo.set_password(password)
            try:
                UserInfo.save()
                # UserProfile = Profile(setup_place=setup_place, setup_day=setup_day, display=display, company_name=company_name, player_serial=player_serial, max_brgt=max_brgt);
                UserProfile.user = UserInfo
                UserProfile.setup_place = setup_place
                UserProfile.setup_day = setup_day
                UserProfile.display = display
                UserProfile.company_name = company_name
                UserProfile.player_serial = player_serial
                UserProfile.max_brgt = max_brgt
                if username =="admin":
                    UserProfile.is_admin = True
                UserProfile.save()
            except:
                pass