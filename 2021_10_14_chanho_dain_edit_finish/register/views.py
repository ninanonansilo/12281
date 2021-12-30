from logging import root
from django.shortcuts import render, redirect
import os, json
from google.cloud import storage
from google.cloud.storage import blob, bucket
from settings.update_json import *
from django.contrib.auth.models import User
from register.models import Profile
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict  # file_data를 생성하기 위해
import json  # json 파일을 위한 확장 라이브러리


# Create your views here.

def register(request):  # register.html 실행 함수
    # get_root_json_from_GCP()
    # read_root_json()
    # add_database()
    userinfo = User.objects.get(username=request.user.username)
    profile = Profile()
    admin_error = ""
    if userinfo.profile.is_admin == True:  # 관리자인 경우 접근가능
        all_db = User.objects.all()
        return render(request, 'register.html', {'userinfo': userinfo, 'profile': profile, 'all_db': all_db})
    if userinfo.profile.is_admin == False: # 관리자가 아닌 경우
        admin_error = "error"
        admin_error_title = "접근 오류"
        admin_error_content = "접근권한이 없습니다"
        return render(request, 'home.html', {'userinfo': userinfo, 'profile': profile,'admin_error_title':admin_error_title, 'admin_error':admin_error,'admin_error_content':admin_error_content})

def users_list(request):  # 조회 버튼을 누르면 사용자 정보들을 불러옴 (사용자 = GCP 버켓 이름)
    return render(request, 'register.html')


def get_root_json_from_GCP(bucket_name="211004-act"):  # download the json
    # always raspi serial is 16 string
    os.system("rm -rf " + top_directory + "root/*")  # initailizing the root file,
    blobs = storage_client.list_blobs(bucket_name)
    for i in blobs:
        if (i.name[17:21] == "root"):
            DOWNLOAD(bucket_name, i.name,
                     top_directory + root_directory + i.name[0:16] + "_root.json")  # download with serial + root.json


def read_root_json():
    json_all_list = os.listdir(top_directory + root_directory)
    json_list = []
    for i in range(len(json_all_list)):
        if (len(json_all_list[i]) > 21):
            json_list.append(json_all_list[i])

    json_info = []
    for i in range(len(json_list)):
        json_list[i] = root_directory + json_list[i]
        with open(json_list[i], 'r', encoding="utf-8-sig") as outfile:
            read_json_info = json.load(outfile)
            json_info.append(read_json_info)


@csrf_exempt
def signup(request):  # 등록
    userinfo = User.objects.get(username=request.user.username)
    profile = Profile()
    all_db = User.objects.all()
    if request.method == "POST":
        UserInfo = User()
        UserProfile = Profile()
        user_id = request.POST["username"]
        user_pw = request.POST["password"]
        user_setup_place = request.POST['setup_place']
        user_setup_day = request.POST['setup_day']
        user_company_name = request.POST['company_name']
        user_display = request.POST['display']
        user_player_serial = request.POST["player_serial"]
        user_max_brgt = request.POST['max_brgt']

        field_error_id = ""  # 아이디 오류
        if user_id == "":
            field_error_id = "아이디를 입력하세요"
        if len(user_id) > 16:
            field_error_id = "최대 16자리 입니다"
        if (str(user_id).islower() == False) or len(str(user_id).split()) > 1:
            field_error_id = "영어 소문자만 입력하세요"

        if User.objects.filter(username=request.POST['username']).exists():
            field_error_id = "이미 존재하는 ID입니다"

        field_error_pw = ""  # 비밀번호 오류
        if user_pw == "":
            field_error_pw = "비밀번호를 입력하세요"
        if len(user_pw) > 16:
            field_error_pw = "최대 16자리 입니다"

        field_error_setup_place = ""  # 설치장소 오류
        if user_setup_place == "":
            field_error_setup_place = "설치장소를 입력하세요"

        field_error_setup_day = ""  # 설치일 오류
        if user_setup_day == "":
            field_error_setup_day = "설치일을 입력하세요"

        else:
            if (user_setup_day.isalpha() == True):
                field_error_setup_day = "형식이 맞지 않습니다."
            else:
                input_to_int = int(''.join(list(filter(str.isdigit, user_setup_day))))
                input_to_int = str(input_to_int)

                if (len(user_setup_day) != 19):
                    field_error_setup_day = "형식이 맞지 않습니다."
                elif (len(input_to_int) != 14):
                    field_error_setup_day = "형식이 맞지 않습니다."
                elif ((user_setup_day[10] != " ")):
                    field_error_setup_day = "형식이 맞지 않습니다."
                elif ((user_setup_day[13] != ":") or (user_setup_day[16] != ":")):
                    field_error_setup_day = "형식이 맞지 않습니다."
                elif ((user_setup_day[4] != "/") or (user_setup_day[7] != "/")):
                    field_error_setup_day = "형식이 맞지 않습니다."



        field_error_company_name = ""  # 업체명 오류
        if user_company_name == "":
            field_error_company_name = "업체명을 입력하세요"

        field_error_display = ""  # 해상도 오류
        if user_display == "":
            field_error_display = "해상도를 입력하세요"

        else:
            if (not list(filter(str.isdigit, user_display))):
                field_error_display = "형식이 맞지 않습니다."
            else:
                input_to_int = int(''.join(list(filter(str.isdigit, user_display))))
                input_to_int = str(input_to_int)
                if(len(user_display) - 1 != len(str(input_to_int))):
                    field_error_display = "형식이 맞지 않습니다."
                elif (user_display[int((len(user_display)-1) / 2)] != "x"):
                    field_error_display = "형식이 맞지 않습니다."
                elif (len(user_display) >=  10):
                    field_error_display = "형식이 맞지 않습니다."
                elif (len(user_display) <  5):
                    field_error_display = "형식이 맞지 않습니다."
                elif (len(user_display) ==  6):
                    field_error_display = "형식이 맞지 않습니다."
                elif (len(user_display) ==  8):
                    field_error_display = "형식이 맞지 않습니다."



        field_error_max_brgt = ""  # 최대밝기 오류
        if user_max_brgt == "":
            field_error_max_brgt = "최대 밝기를 입력하세요"


        if (user_max_brgt.isdigit() == False):
            field_error_max_brgt = "형식이 맞지 않습니다."

        elif (int(user_max_brgt) > 63):
            field_error_max_brgt =  "형식이 맞지 않습니다."
        elif (int(user_max_brgt) < 0):
            field_error_max_brgt = "형식이 맞지 않습니다."


        field_error_player_serial = ""  # 시리얼 오류
        if user_player_serial == "":
            field_error_player_serial = "Serial을 입력하세요"

        if field_error_id != "" or field_error_pw != "" or field_error_setup_place != "" or field_error_setup_day != "" or field_error_company_name != "" or field_error_display != "" or field_error_max_brgt != "" or field_error_player_serial != "":  # 오류가 있는 경우 반환
            return render(request, 'register.html',
                          {'userinfo': userinfo, 'profile': profile, 'all_db': all_db, 'username': user_id,
                           'password': user_pw,
                           'user_setup_place': user_setup_place, 'user_setup_day': user_setup_day,
                           'user_company_name': user_company_name, 'user_display': user_display,
                           'user_max_brgt': user_max_brgt, 'user_player_serial': user_player_serial,
                           'field_error': field_error_id, 'field_error_pw': field_error_pw,
                           'field_error_setup_place': field_error_setup_place,
                           'field_error_setup_day': field_error_setup_day,
                           'field_error_company_name': field_error_company_name,
                           'field_error_display': field_error_display, 'field_error_max_brgt': field_error_max_brgt,
                           'field_error_player_serial': field_error_player_serial})
        else:
            if Profile.objects.filter(player_serial=request.POST['player_serial']).exists():
                id = request.POST["hidden_id"]
                print(id)
                User.objects.filter(username=id).delete()

            UserInfo.username = user_id
            password = user_pw
            UserInfo.set_password(password)
            try:
                UserInfo.save()
                UserProfile.user = UserInfo
                UserProfile.setup_place = user_setup_place
                UserProfile.setup_day = user_setup_day
                UserProfile.display = user_display
                UserProfile.company_name = user_company_name
                UserProfile.player_serial = user_player_serial
                UserProfile.max_brgt = user_max_brgt
                UserProfile.save()

                file_data = OrderedDict()
                file_data["id"] = user_id
                file_data["pw"] = user_pw
                file_data["setup_place"] = user_setup_place
                split_day = re.split(r'/|:| ', user_setup_day)
                file_data["setup_day"] = {'year': split_day[0], 'month': split_day[1], 'day': split_day[2],
                                          'hour': split_day[3], 'minute': split_day[4], 'second': split_day[5]}
                user_display = re.split(r'x', user_display)
                file_data["display"] = {'width': user_display[0], 'height': user_display[1]}
                file_data["max_brightness"] = user_max_brgt
                file_data["serial"] = user_player_serial
                file_data["company_name"] = user_company_name

                with open('root.json', 'w', encoding="utf-8") as make_file:
                    json.dump(file_data, make_file, ensure_ascii=False, indent="\t")

                UPLOAD("211004-act", "root.json", user_player_serial + "/root.json")

            except:
                pass

    all_db = User.objects.all()
    return render(request, 'login.html')


@csrf_exempt
def read_root_json():
    json_list = os.listdir(top_directory + root_directory)
    # json_list = []
    # for i in range(len(json_all_list)):
    #     if(json_all_list[i] != 'all_player.json'):
    #         json_list.append(json_all_list[i])
    json_info = []
    for i in range(len(json_list)):
        json_list[i] = root_directory + json_list[i]
        with open(json_list[i], 'r', encoding="utf-8-sig") as outfile:
            read_json_info = json.load(outfile)
            json_info.append(read_json_info)
    # with open(top_directory + root_directory + "all_player.json", 'w', encoding="utf-8-sig") as inputfile:
    #     json.dump(json_info, inputfile, indent=4, ensure_ascii=False) # not broken korean, ensure..


@csrf_exempt
def show_root_json():
    with open(top_directory + root_directory + "all_player.json", 'r', encoding='utf-8-sig') as info:
        root_info = json.load(info)
        id_info = []
        pw_info = []
        setup_place = []
        setup_date = []
        company_name = []
        display = []
        max_brgt = []
        serial_number = []
        for i in range(len(root_info)):
            id_info.append(root_info[i]["id"])
            pw_info.append(root_info[i]["pw"])
            setup_place.append(root_info[i]["setup_place"])
            year = int(root_info[i]["setup_day"]["year"]);
            month = int(root_info[i]["setup_day"]["month"]);
            day = int(root_info[i]["setup_day"]["day"]);
            hour = int(root_info[i]["setup_day"]["hour"]);
            minute = int(root_info[i]["setup_day"]["minute"]);
            second = int(root_info[i]["setup_day"]["second"]);
            setup_date.append(datetime.datetime(year, month, day, hour, minute, second).strftime('%Y/%m/%d %H:%M:%S'))
            company_name.append(root_info[i]["company_name"]);
            display.append(root_info[i]["display"]["width"] + 'x' + root_info[i]["display"]["height"]);
            max_brgt.append(int(root_info[i]["max_brightness"]));
            serial_number.append(root_info[i]["serial"]);
            # day3 = datetime.datetime(2020, 12, 14, 14, 10, 50).strftime('%Y-%m-%d %H:%M:%S')

        return id_info, pw_info, setup_place, setup_date, company_name, display, max_brgt, serial_number, root_info


@csrf_exempt
def apply_new_json(user_id, user_pw, user_setup_place, user_setup_day, user_company_name, user_display, user_brgt,
                   user_serial):
    info = {}
    info["id"] = str(user_id)
    info['pw'] = str(user_pw);
    info["setup_place"] = str(user_setup_place)
    info["setup_day"] = {};
    info["setup_day"]["year"] = str(user_setup_day)[:4]
    info["setup_day"]["month"] = str(user_setup_day)[5:7];
    info["setup_day"]["day"] = str(user_setup_day)[8:10]
    info["setup_day"]["hour"] = str(user_setup_day)[11:13];
    info["setup_day"]["minute"] = str(user_setup_day)[14:16]
    info["setup_day"]["second"] = str(user_setup_day)[17:19]
    info["display"] = {};
    user_width, user_height = str(user_display).split('x')
    info["display"]["width"] = str(user_width);
    info["display"]["height"] = str(user_height)
    info["max_brightness"] = str(user_brgt);
    info["serial"] = str(user_serial)
    info["company_name"] = str(user_company_name)
    with open(top_directory + root_directory + str(user_serial) + "_root.json", 'w', encoding='utf-8-sig') as json_info:
        json.dump(info, json_info, indent=4, ensure_ascii=False)
