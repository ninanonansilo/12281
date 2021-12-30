from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from settings.update_json import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from imgn.make_timetable import *
from PIL import ImageColor
from imgn.media_json import *
from urllib import parse
import numpy as np
from time import time
import os
from django.contrib.auth.models import User
from register.models import Profile
#-------------------- for text preview -------------------
from PIL import Image, ImageFont, ImageDraw
from django.contrib import messages
#---------------------------------------------------------
#from django.utils import simplejson
# Create your views here.
def imgn(request):  # 페이지 로딩시 리스트에 이미지, 문자 올림
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial
    profile = Profile()
    admin_error = ""
    if userinfo.profile.is_admin == True:  # 관리자인 경우 접근불가
        admin_error = "error"
        admin_error_title = "접근 오류"
        admin_error_content = "접근권한이 없습니다"
        return render(request, 'home.html', {'userinfo': userinfo, 'profile': profile,'admin_error_title':admin_error_title, 'admin_error':admin_error,'admin_error_content':admin_error_content})
        messages.warning(request, "접근권한이 없습니다")
        return render(request, 'home.html', {'userinfo': userinfo, 'profile': profile})
    if userinfo.profile.is_admin == False:  # 관리자가 아닌 경우

        img_list = img_list_in_bucket(user_id)  # 버켓안에 최신파일 이름 받아옴

        userinfo.profile.var_picture_index = -1
        userinfo.profile.var_text_index = -1

        print("현재 저장된 이미지 목록->")
        print(img_list) # 저장된 이미지 리스트
        img_time_list = []
        img_name_list = []
        text_time_list = []
        text_name_list = []

        for i in range(len(img_list)): # img_list에서 시간이랑 이미지 이름 분리
            len_t = int(img_list[i][14]) # (지속시간 길이)
            img_time_list.append(str(img_list[i][15: 14 + len_t+1])) # 파일 이름 앞에 지속시간 분리 (첫자리 제외)
            img_name_list.append(str(img_list[i][14 + len_t+1:])) # 나머지 파일이름 따로 저장

        text_list = text_list_in_bucket(user_id)
        for i in range(len(text_list)):
            len_t = int(text_list[i][14]) # (지속시간 길이)
            text_time_list.append(str(text_list[i][15: 14 + len_t+1])) # 파일 이름 앞에 지속시간 분리 (첫자리 제외)
            text_name_list.append(str(text_list[i][14 + len_t+1:])) # 나머지 파일이름 따로 저장

        print("현재 저장된 문자 목록->")
        print(text_list) # 저장된 문자 리스트

        list_dict = {
            'img_name' : img_name_list,
            'img_time' : img_time_list,
            'text_name' : text_name_list,
            'text_time' : text_time_list,
            'user_id' : user_id,
            'picture_index' : userinfo.profile.var_picture_index,
            'text_index':userinfo.profile.var_text_index,
        }
        context = json.dumps(list_dict)
        userinfo = User.objects.get(username=request.user.username)
        return render(request, 'image.html', {'context': context, 'userinfo':userinfo, 'user_id': user_id,})

@csrf_exempt
def upload_img(request):
    print("호출 성공")
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            stay_time = request.POST['time']    # 지속시간
            img_name = request.POST['img_name']  # 이미지 이름
            print(stay_time)
            img = request.FILES.get('img')  # 이미지를 request에서 받아옴
            path = default_storage.save(user_id +"/img.jpg", ContentFile(img.read()))
            now_kst = time_now()
            UPLOAD(using_bucket, user_id + "/img.jpg", user_id + "/IMAGE/" + now_kst.strftime("%Y%m%d%H%M%S") + str(len(stay_time)) + str(stay_time) + img_name)
            os.remove(user_id+"/img.jpg") # 장고에서 중복된 이름의 파일에는 임의로 이름을 변경하기 때문에 임시파일은 제거
            return redirect('image.html')
        else:
            print("ajax 통신 실패!")
            return redirect('image.html')
    else:
        print("POST 호출 실패!")
        return redirect('image.html')

@csrf_exempt
def downmove_picture(request):
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial
    img_list = img_list_in_bucket(user_id)

    this_picture_index = int(request.POST['picture_index'])
    userinfo.profile.var_picture_index  = this_picture_index + 1
    next_picture_index = this_picture_index + 1

    this_picture = img_list[this_picture_index]
    next_picture = img_list[this_picture_index + 1]
    this_picture_makedate = img_list[this_picture_index][:14]
    this_picture_name = img_list[this_picture_index][14:]
    next_picture_makedate = img_list[next_picture_index][:14]
    next_picture_name = img_list[next_picture_index][14:]


    rename_blob(using_bucket,
                user_id + "/IMAGE/" + this_picture,
                user_id + "/IMAGE/" + next_picture_makedate + this_picture_name)

    rename_blob(using_bucket,
                user_id + "/IMAGE/" + next_picture,
                user_id + "/IMAGE/" + this_picture_makedate + next_picture_name)

    return redirect('image.html')

@csrf_exempt
def upmove_picture(request):
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial
    img_list = img_list_in_bucket(user_id)

    this_picture_index = int(request.POST['picture_index'])
    userinfo.profile.var_picture_index  = this_picture_index - 1 #재로딩될때 인덱스를 위한 지역변수임
    pre_picture_index = this_picture_index - 1

    this_picture = img_list[this_picture_index]
    pre_picture = img_list[pre_picture_index]
    this_picture_makedate = img_list[this_picture_index][:14]
    this_picture_name = img_list[this_picture_index][14:]
    pre_picture_makedate = img_list[pre_picture_index][:14]
    pre_picture_name = img_list[pre_picture_index][14:]


    rename_blob(using_bucket,
                user_id + "/IMAGE/" + this_picture,
                user_id + "/IMAGE/" + pre_picture_makedate + this_picture_name)

    rename_blob(using_bucket,
                user_id + "/IMAGE/" + pre_picture,
                user_id + "/IMAGE/" + this_picture_makedate + pre_picture_name)

    return redirect('image.html')

@csrf_exempt
def downmove_letter(request):
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial
    text_list = text_list_in_bucket(user_id)

    this_text_index = int(request.POST['letter_index'])
    userinfo.profile.var_text_index = this_text_index + 1
    next_text_index = this_text_index + 1

    this_text = text_list[this_text_index]
    next_text = text_list[this_text_index + 1]
    this_text_makedate = text_list[this_text_index][:14]
    this_text_name = text_list[this_text_index][14:]
    next_text_makedate = text_list[next_text_index][:14]
    next_text_name = text_list[next_text_index][14:]


    rename_blob(using_bucket,
                user_id + "/JSON/TEXT_LIST/" + this_text,
                user_id + "/JSON/TEXT_LIST/" + next_text_makedate + this_text_name)

    rename_blob(using_bucket,
                user_id + "/JSON/TEXT_LIST/" + next_text,
                user_id + "/JSON/TEXT_LIST/" + this_text_makedate + next_text_name)
    return redirect('image.html')

@csrf_exempt
def upmove_letter(request):
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial

    text_list = text_list_in_bucket(user_id)

    this_text_index = int(request.POST['letter_index'])
    userinfo.profile.var_text_index = this_text_index - 1
    pre_text_index = this_text_index - 1

    this_text = text_list[this_text_index]
    pre_text = text_list[this_text_index - 1]
    this_text_makedate = text_list[this_text_index][:14]
    this_text_name = text_list[this_text_index][14:]
    pre_text_makedate = text_list[pre_text_index][:14]
    pre_text_name = text_list[pre_text_index][14:]

    rename_blob(using_bucket,
                user_id + "/JSON/TEXT_LIST/" + this_text,
                user_id + "/JSON/TEXT_LIST/" + pre_text_makedate + this_text_name)

    rename_blob(using_bucket,
                user_id + "/JSON/TEXT_LIST/" + pre_text,
                user_id + "/JSON/TEXT_LIST/" + this_text_makedate + pre_text_name)
    return redirect('image.html')

@csrf_exempt
def save_letter(request): # 문자 설정 -> 확인 버튼 눌렀을 시 // 버켓 안 TEXT_LIST 디렉토리에 업로드하여 저장 (TIMETABLE을)
    if request != "":
        print("========= 시작 ===========")
        userinfo = User.objects.get(username=request.user.username)
        user_id = userinfo.profile.player_serial

        change = request_body_list_text(request.body)
        change[9] = parse.unquote(change[9])

        data = make_Timetable_text()
        now_kst = time_now()  # 현재시간 받아옴
        now_kst1 = time_now()
        now_kst = now_kst + timedelta(seconds=15)

        data[4]["detail_info"]["x"] = str(change[1])
        data[4]["detail_info"]["y"] = str(change[2])
        data[4]["detail_info"]["width"] = str(change[3])
        data[4]["detail_info"]["height"] = str(change[4])
        data[4]["detail_info"]["play_speed"] = str(change[5])
        data[4]["detail_info"]["play_count"] = str(change[6])
        data[4]["detail_info"]["font_size"] = str(change[7])     # 폰트사이즈 - 인터페이스 수정 전까지 고정시킴
        data[4]["detail_info"]["scroll_fix"] = str(change[10])
        data[4]["detail_info"]["play_second"] = str(change[11])
        data[4]["detail_info"]["thickness_italics"] = str(change[12])

        data[4]["title"] = str(change[0])
        data[4]["title"] = parse.unquote(data[4]["title"])

        hex = str("#" + change[8])
        rgb_value = ImageColor.getcolor(hex,"RGB")
        data[4]["detail_info"]["red_green_blue"] = str(rgb_value)

        data[4]["time"]["year"] = now_kst.strftime("%Y").zfill(4)
        data[4]["time"]["month"] = now_kst.strftime("%m").zfill(2)
        data[4]["time"]["day"] = now_kst.strftime("%d").zfill(2)
        data[4]["time"]["hour"] = now_kst.strftime("%H").zfill(2)
        data[4]["time"]["minute"] = now_kst.strftime("%M").zfill(2)
        data[4]["time"]["second"] = now_kst.strftime("%S").zfill(2)

        if (str(change[10]) == '0'): # 스크롤 경우
            title = str(change[0])
            len_text = len(title)
            all_text_pixel = int(0.9 * int(len_text) * int(data[4]["detail_info"]["font_size"])) - int(change[3])
            micro_second = (all_text_pixel * 100) / int(change[5]) # 100 is ms
            ans = int(np.rint((micro_second / 1000) * int(change[6])))
            now_kst = now_kst + timedelta(seconds=15) + timedelta(seconds=ans)
            time_code = str(len(str(ans))) + str(ans)
        elif (str(change[10]) == '1'):  # 고정 경우
            now_kst = now_kst + timedelta(seconds=15) + timedelta(seconds=(int(change[11])))
            time_code = str(len(str(change[11]))) + str(change[11])
        else:
            print("스크롤-고정 선택 오류")
            return redirect('image.html')

        createDirectory(user_id)
        save_file(user_id, data)
        UPLOAD(using_bucket, user_id+"/send" , user_id + "/JSON/TEXT_LIST/" + now_kst1.strftime("%Y%m%d%H%M%S") + time_code + str(change[9]))

        return redirect('image.html')
    else:
        return redirect('image.html')

@csrf_exempt
def edit_letter(request): # 문자편집
    if request != "":
        print("========= 시작 ===========")
        userinfo = User.objects.get(username=request.user.username)
        user_id = userinfo.profile.player_serial

#삭제 먼저!!
        delete_index = int(request.POST['index'])

        #delete_index += 1  # 다인이 작성한 인덱스 반환이 -1부터 시작하여 1을 더함
        #print(delete_index)
        text_list = text_list_in_bucket(user_id)
        print(text_list)
        if (delete_index >= len(text_list)): #
            return redirect('image.html')
        else:
            delete_name = text_list[delete_index]  # 삭제할 파일 이름 (고유번호 포함)
            print(delete_name)
            delete_blob(using_bucket, user_id + "/JSON/TEXT_LIST/" + delete_name)
            exiting_time = delete_name[:14]



        text_name_list = []
        text_list = text_list_in_bucket(user_id)
        for i in range(len(text_list)):
            len_t = int(text_list[i][14])  # (지속시간 길이)
            text_name_list.append(str(text_list[i][14 + len_t + 1:]))  # 나머지 파일이름 따로 저장

        change = request_body_list_text(request.body)
        change[9] = parse.unquote(change[9])
        change[0] = parse.unquote(change[0])

        index = int(change[12])

        data = make_Timetable_text()
        now_kst = time_now()  # 현재시간 받아옴

        now_kst = now_kst + timedelta(seconds=15)

        data[4]["detail_info"]["x"] = str(change[1])
        data[4]["detail_info"]["y"] = str(change[2])
        data[4]["detail_info"]["width"] = str(change[3])
        data[4]["detail_info"]["height"] = str(change[4])
        data[4]["detail_info"]["play_speed"] = str(change[5])
        data[4]["detail_info"]["play_count"] = str(change[6])
        data[4]["detail_info"]["font_size"] = str(change[7])     # 폰트사이즈 - 인터페이스 수정 전까지 고정시킴
        data[4]["detail_info"]["scroll_fix"] = str(change[10])
        data[4]["detail_info"]["play_second"] = str(change[11])

        data[4]["title"] = str(change[0])
        hex = str("#" + change[8])
        rgb_value = ImageColor.getcolor(hex,"RGB")
        data[4]["detail_info"]["red_green_blue"] = str(rgb_value)

        data[4]["time"]["year"] = now_kst.strftime("%Y").zfill(4)
        data[4]["time"]["month"] = now_kst.strftime("%m").zfill(2)
        data[4]["time"]["day"] = now_kst.strftime("%d").zfill(2)
        data[4]["time"]["hour"] = now_kst.strftime("%H").zfill(2)
        data[4]["time"]["minute"] = now_kst.strftime("%M").zfill(2)
        data[4]["time"]["second"] = now_kst.strftime("%S").zfill(2)

        # 지속시간 계산
        if (str(change[10]) == '0'): # 스크롤 경우
            title = str(change[0])
            len_text = len(title)
            all_text_pixel = int(0.9 * int(len_text) * int(data[4]["detail_info"]["font_size"])) - int(change[3])
            micro_second = (all_text_pixel * 100) / int(change[5]) # 100 is ms
            ans = int(np.rint((micro_second / 1000) * int(change[6])))
            now_kst = now_kst + timedelta(seconds=15) + timedelta(seconds=ans)
            time_code = str(len(str(ans))) + str(ans)
        elif (str(change[10]) == '1'):  # 고정 경우
            now_kst = now_kst + timedelta(seconds=15) + timedelta(seconds=(int(change[11])))
            time_code = str(len(str(change[11]))) + str(change[11])
        else:
            print("스크롤-고정 선택 오류")
            return redirect('image.html')

        createDirectory(user_id)
        save_file(user_id, data)
        UPLOAD(using_bucket, user_id+"/send" , user_id + "/JSON/TEXT_LIST/" + exiting_time + time_code + str(change[9]))

        return redirect('image.html')
    else:
        return redirect('image.html')


@csrf_exempt
def event_trans(request):    # 이벤트 전송 버튼 TEXT_LIST에서 선택된 TIMETABLE을 JSON/TIMETABLE로 전송
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial


    check_list_text = value_of_request_body_list(request.body) # 선택된 파일 인덱스

    blobs = storage_client.list_blobs(using_bucket)
    ############ 이미지 정보 ############
    list_blob_img = []
    list_blob_text = []
    except_str = str(user_id + "/IMAGE/")  # 제외시킬 문자열
    except_str1 = str(user_id + "/JSON/TEXT_LIST/")  # 제외시킬 문자열
    for blob in blobs:
        if blob.name.startswith(except_str):
            blob.name = blob.name.replace(except_str, '')
            if (len(blob.name) < 2):
                pass
            else:
                list_blob_img.append(blob.name)
        if blob.name.startswith(except_str1):
            blob.name = blob.name.replace(except_str1, '')
            if (len(blob.name) < 2):
                pass
            else:
                list_blob_text.append(blob.name)
    print(list_blob_text)
    #if (len(list_blob_img)) >= 2:
    #    list_blob_img.pop(0)
    #if (len(list_blob_text)) >= 2:
    #    list_blob_text.pop(0)

    call_text = []  # TEXT_LIST에서 선택된 문자를 담을 리스트
    call_img = []

    for index in range(40):
        if index < 20:  # 문자
            if check_list_text[index] != '':  # 체크된 인덱스
                if len(list_blob_text) > (index):  # 이미 업로드된 범위 내의 체크
                    call_text.append(list_blob_text[index])
                else:
                    pass
        else: # 이미지
            if check_list_text[index] != '':  # 체크된 인덱스
                if len(list_blob_img) > (index-20):  # 이미 업로드된 범위 내의 체크
                    call_img.append((list_blob_img[index-20]))
                else:
                    pass


    print("오류확인용 ##############@@@@@@@@@@@@@@@@")
    print(list_blob_img)
    print(list_blob_text)

    data = []
    now_kst = time_now()  # 현재시간 받아옴
    now_kst = now_kst + timedelta(seconds=15)
    now_kst1 = time_now()  # 현재시간 받아옴
    cum_time = 0
    sort_time = []

    for i in range(len(call_img)):  # 사진목록의 타임테이블 작성
        now_kst = now_kst + timedelta(seconds= cum_time)
        # 시간 추출 부분

        len_t = int(call_img[i][14])  # (지속시간 길이)

        img_time = (str(call_img[i][15: 14 + len_t + 1]))  # 파일 이름 앞에 지속시간 분리 (첫자리 제외)
        img_name = (str(call_img[i][14 + len_t + 1:]))  # 나머지 파일이름 따로 저장

        # 파일이름만 추가
        info = {}
        info["time"] = {}
        info["time"]["year"] = now_kst.strftime("%Y").zfill(4)
        info["time"]["month"] = now_kst.strftime("%m").zfill(2)
        info["time"]["day"] = now_kst.strftime("%d").zfill(2)
        info["time"]["hour"] = now_kst.strftime("%H").zfill(2)
        info["time"]["minute"] = now_kst.strftime("%M").zfill(2)
        info["time"]["second"] = now_kst.strftime("%S").zfill(2)
        info["time"]["alltime"] = now_kst.strftime("%Y").zfill(4) + now_kst.strftime("%m").zfill(2) + now_kst.strftime(
            "%d").zfill(2) + now_kst.strftime("%H").zfill(2) + now_kst.strftime("%M").zfill(2) + now_kst.strftime(
            "%S").zfill(2)
        sort_time.append(int(info["time"]["alltime"]))
        info["type"] = "image"
        info["action"] = "play"
        info["title"] = str(img_name)
        data.append(info)
        now_kst = now_kst + timedelta(seconds=(int(img_time)))

        info = {}
        info["time"] = {}
        info["time"]["year"] = now_kst.strftime("%Y").zfill(4)
        info["time"]["month"] = now_kst.strftime("%m").zfill(2)
        info["time"]["day"] = now_kst.strftime("%d").zfill(2)
        info["time"]["hour"] = now_kst.strftime("%H").zfill(2)
        info["time"]["minute"] = now_kst.strftime("%M").zfill(2)
        info["time"]["second"] = now_kst.strftime("%S").zfill(2)
        info["time"]["alltime"] = now_kst.strftime("%Y").zfill(4) + now_kst.strftime("%m").zfill(2) + now_kst.strftime(
            "%d").zfill(2) + now_kst.strftime("%H").zfill(2) + now_kst.strftime("%M").zfill(2) + now_kst.strftime(
            "%S").zfill(2)
        sort_time.append(int(info["time"]["alltime"]))
        info["type"] = "image"
        info["action"] = "stop"
        data.append(info)

        cum_time += int(img_time) + 1
        # 해당 이미지 media/image/로 업로드
        copy_blob(using_bucket, user_id + "/IMAGE/" + str(call_img[i]), using_bucket,
                  user_id + "/MEDIA/image/" + str(img_name))

    cum_time = 0

    for i in range(len(call_text)):   # 텍스트 부분

        DOWNLOAD(using_bucket, user_id + "/JSON/TEXT_LIST/" + call_text[i], user_id + "/temp")
        text_setting = read_json(user_id)

        cum_time += 1
        now_kst = now_kst + timedelta(seconds=(int(cum_time)))
        print(text_setting)
        print(text_setting)
        print(text_setting)
        print(text_setting)
        info = {}
        info["time"] = {}
        info["detail_info"] = {}
        info["detail_info"]["x"] = text_setting[4]["detail_info"]["x"]
        info["detail_info"]["y"] = text_setting[4]["detail_info"]["y"]
        info["detail_info"]["width"] = text_setting[4]["detail_info"]["width"]
        info["detail_info"]["height"] = text_setting[4]["detail_info"]["height"]
        info["detail_info"]["scroll_fix"] = text_setting[4]["detail_info"]["scroll_fix"]
        info["detail_info"]["play_speed"] = text_setting[4]["detail_info"]["play_speed"]
        info["detail_info"]["play_count"] = text_setting[4]["detail_info"]["play_count"]
        info["detail_info"]["font_name"] = "NanumGothic"  # 추가필요
        info["detail_info"]["font_size"] = text_setting[4]["detail_info"]["font_size"]
        info["detail_info"]["play_second"] = text_setting[4]["detail_info"]["play_second"]
        info["detail_info"]["thickness_italics"] = text_setting[4]["detail_info"]["thickness_italics"]
        info["detail_info"]["red_green_blue"] = text_setting[4]["detail_info"]["red_green_blue"]

        info["time"] = {}
        info["time"]["year"] = now_kst.strftime("%Y").zfill(4)
        info["time"]["month"] = now_kst.strftime("%m").zfill(2)
        info["time"]["day"] = now_kst.strftime("%d").zfill(2)
        info["time"]["hour"] = now_kst.strftime("%H").zfill(2)
        info["time"]["minute"] = now_kst.strftime("%M").zfill(2)
        info["time"]["second"] = now_kst.strftime("%S").zfill(2)
        info["time"]["alltime"] = now_kst.strftime("%Y").zfill(4) + now_kst.strftime("%m").zfill(2) + now_kst.strftime(
            "%d").zfill(2) + now_kst.strftime("%H").zfill(2) + now_kst.strftime("%M").zfill(2) + now_kst.strftime(
            "%S").zfill(2)
        sort_time.append(int(info["time"]["alltime"]))

        info["title"] = text_setting[4]["title"]
        info["type"] = "string"
        info["action"] = "play"
        data.append(info)

        if (str(text_setting[4]["detail_info"]["scroll_fix"]) == '0'):  # 스크롤
            title = str(text_setting[4]["title"])
            len_text = len(title)
            all_text_pixel = int(0.9 * int(len_text) * int(text_setting[4]["detail_info"]["font_size"])) - int(
                text_setting[4]["detail_info"]["width"])
            micro_second = (all_text_pixel * 100) / int(text_setting[4]["detail_info"]["play_speed"])  # 100 is ms
            ans = np.rint((micro_second / 1000) * int(text_setting[4]["detail_info"]["play_count"]))
            now_kst = now_kst + timedelta(seconds=(int(ans))) + timedelta(seconds=1)
            cum_time += (ans + 1)
        elif (str(text_setting[4]["detail_info"]["scroll_fix"]) == '1'):  # 고정
            now_kst = now_kst + timedelta(seconds= (int(text_setting[4]["detail_info"]["play_second"]) + 1))
            cum_time += (int(text_setting[4]["detail_info"]["play_second"]) + 1)

        info = {}
        info["time"] = {}
        info["time"]["year"] = now_kst.strftime("%Y").zfill(4)
        info["time"]["month"] = now_kst.strftime("%m").zfill(2)
        info["time"]["day"] = now_kst.strftime("%d").zfill(2)
        info["time"]["hour"] = now_kst.strftime("%H").zfill(2)
        info["time"]["minute"] = now_kst.strftime("%M").zfill(2)
        info["time"]["second"] = now_kst.strftime("%S").zfill(2)
        info["time"]["alltime"] = now_kst.strftime("%Y").zfill(4) + now_kst.strftime("%m").zfill(2) + now_kst.strftime(
            "%d").zfill(2) + now_kst.strftime("%H").zfill(2) + now_kst.strftime("%M").zfill(2) + now_kst.strftime(
            "%S").zfill(2)
        sort_time.append(int(info["time"]["alltime"]))

        info["type"] = "string"
        info["action"] = "stop"


        data.append(info)
    # 추가) 기존의 타임테이블 가져와서 시간 중복 처리########################################

    # 최신 타임테이블을 가져옴
    #timetable_list = timetable_list_in_bucket(user_id)
    #DOWNLOAD(using_bucket, user_id + "/JSON/TIMETABLE/" + timetable_list[-1] ,  user_id+ "/timetable")
    #list_json = read_timetable(user_id) # 최근 타임테이블
    #if list_json is None:
    #    list_json = []

    #print(list_json[0]['time']['alltime'])
    sort_time.sort() # 이미지 + 텍스트 => 시작 시간, 끝나는 시간
    #print(list_json)
    #for i in range(0, len(list_json), 2):
        #if (int(list_json[i]['time']["alltime"]) <= sort_time[0]): # 끼어들어야 하는 경우
            #if (int(list_json[i+1]['time']["alltime"]) > sort_time[-1]): # 그사이에 끝나는 경우
                #list_json[i+1]['time']["alltime"] = str(sort_time[-1])
            #else: # 다음거 침범
                #list_json[i+2]['time']["alltime"] = str(sort_time[-1] + 5)
        #else:
            #pass

    #list_json.extend(data)

    ################################################################################

    save_file(user_id, data)
    UPLOAD(using_bucket, user_id + "/send",
           user_id + "/JSON/TIMETABLE/" + now_kst1.strftime("%Y%m%d%H%M%S"))

    return render(request, 'image.html')

# 사진 GCP에서 다운해서 폴더 home/static에 저장 하는 코드
@csrf_exempt
def save_img(request):
    print("이미지 저장 호출 성공")
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial


    img_list = img_list_in_bucket(user_id)
    change = int(request.POST['miribogi'])
    if os.path.isfile("home//static//" + user_id + "_img.jpg"):
        os.remove("home//static//" + user_id + "_img.jpg")
    DOWNLOAD(using_bucket, user_id + "/IMAGE/{}".format(img_list[change]), "home//static//" + user_id + "_img.jpg")
    # 사진 저장도 인덱스.jpg ex) 0.jpg 1.jpg 형식으로 저장함

    return redirect('image.html')



@csrf_exempt
def delete_img(request):
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            delete_index = int(request.POST['index'])
            delete_index += 1 # 다인이 작성한 인덱스 반환이 -1부터 시작하여 1을 더함
            img_list = img_list_in_bucket(user_id)

            if (delete_index >= len(img_list)):
                pass
            else:
                delete_name = img_list[delete_index]  # 삭제할 파일 이름 (고유번호 포함)
                delete_blob(using_bucket, user_id + "/IMAGE/" + delete_name)

            return redirect('image.html')
        else:
            print("ajax 통신 실패!")
            return redirect('image.html')
    else:
        print("POST 호출 실패!")
        return redirect('image.html')


    return redirect('image.html')



@csrf_exempt
def delete_text(request):
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            delete_index = int(request.POST['index'])
            delete_index += 1 # 다인이 작성한 인덱스 반환이 -1부터 시작하여 1을 더함
            text_list = text_list_in_bucket(user_id)
            if (delete_index >= len(text_list)):
                pass
            else:
                delete_name = text_list[delete_index]  # 삭제할 파일 이름 (고유번호 포함)
                delete_blob(using_bucket, user_id + "/JSON/TEXT_LIST/" + delete_name)

            return redirect('image.html')
        else:
            print("ajax 통신 실패!")
            return redirect('image.html')
    else:
        print("POST 호출 실패!")
        return redirect('image.html')


    return redirect('image.html')


#-------------------- for text preview -------------------
def make_text_preview(user_id , text_data): # 텍스트 미리보기
   print("--------------------> make_text_preview is called <--------------------")

   text_content = text_data[4]['title']
   axis_x = int(text_data[4]['detail_info']['x'])
   axis_y = int(text_data[4]['detail_info']['y'])
   axis_w = int(text_data[4]['detail_info']['width'])
   axis_h = int(text_data[4]['detail_info']['height'])
   play_speed = int(text_data[4]['detail_info']["play_speed"])
   play_count = int(text_data[4]['detail_info']["play_count"])
   font_size = int(text_data[4]['detail_info']["font_size"])
   scroll_fix = int(text_data[4]['detail_info']["scroll_fix"])
   play_second = int(text_data[4]['detail_info']["play_second"])
   rgb_value_str = text_data[4]['detail_info']["red_green_blue"] # 튜플 형식이 문자열로 왔기 때문에 다시 튜플 형식으로 바꾸는 작업 필요
   splited_rgb = rgb_value_str.split(',')
   rgb_value = (int(re.sub(r'[^0-9]', '', splited_rgb[0])),int(re.sub(r'[^0-9]', '', splited_rgb[1])),int(re.sub(r'[^0-9]', '', splited_rgb[2])))
   rgb = str(rgb_value)

   print("--------------------> make_text_preview : parameter list and value <--------------------")
   print("text content: " + text_content)
   print("axis x: " + str(axis_x))
   print("axis y: " + str(axis_y))
   print("axis w: " + str(axis_w))
   print("axis h: " + str(axis_h))
   print("play speed: " + str(play_speed))
   print("play count: " + str(play_count))
   print("font size: " + str(font_size))
   print("scroll fixed: " + str(scroll_fix))
   print("font color: " + rgb)

   if axis_x < 0:
      axis_x = 0
   if axis_y < 0:
      axis_y = 0
   if axis_w < 1:
      axis_w = 1
   if axis_h < 1:
      axis_h = 1
   if not text_content:
      text_content = "ActVision"

   font = "NanumGothic"
   thickness_italics = 0
   background_color = (255, 255, 255)
   text_color = rgb_value

   if os.path.exists("home/static/text_preview.jpg"):
      os.remove("home/static/text_preview.jpg")

   if(font == "NotoSansCJK-Regular.ttc"):
      font = ImageFont.truetype("/usr/share/fonts/opentype/noto/" + font, int(font_size))

   elif(font == "FreeSerif"):
      if(thickness_italics == 0):
         font = ImageFont.truetype("/home/font/FreeSerif.ttf", int(font_size))
      elif(thickness_italics == 1):
         font = ImageFont.truetype("/home/font/FreeSerifBold.ttf", int(font_size))
      elif(thickness_italics == 2):
         font = ImageFont.truetype("/home/font/FreeSerifItalic.ttf", int(font_size))
         # elif(thickness_italics == 3):
         #     font = ImageFont.truetype("/home/pi/EV/FONTS/FreeSerif/FreeSerifBoldItalic.ttf", int(font_size))
   elif(font == "NanumGothic"):
      if(thickness_italics == 0):
         font = ImageFont.truetype("home/font/NanumGothic.ttf", int(font_size))
      else: #if(thickness_italics == 1):
         font = ImageFont.truetype("home/font/NanumGothicBold.ttf", int(font_size))

   im = Image.new('RGB', (axis_w, axis_h), background_color)
   drawer = ImageDraw.Draw(im)
   drawer.text((axis_x, axis_y), text_content, font=font, fill=text_color)

   if axis_w <= 1 or axis_h <= 1:
   # text_height = font_size
      (text_width, text_height) = drawer.textsize(text=text_content, font=font)
      print("--------------------> text width is {}".format(text_width))
      print("--------------------> text height is {}".format(text_height))
      im = Image.new('RGB', (text_width, text_height), background_color)
      drawer = ImageDraw.Draw(im)
      drawer.text((axis_x, axis_y), text_content, font=font, fill=text_color)
   im.save("home/static/" + user_id + "_text.jpg")
   print("preview image is saved....")

   return 0


@csrf_exempt
def session_text_json(request):  # 문자를 선택하면 JSON 데이터를 받아와 세션(쿠키)에 저장 -> 일단 세션 사용하지 않고 구현
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            text_index = int(request.POST['index'])
            text_list = text_list_in_bucket(user_id)
            selected_text_name = text_list[text_index]
            DOWNLOAD(using_bucket, user_id + "/JSON/TEXT_LIST/" + selected_text_name , user_id + "/checked_text")
            with open(user_id + '/checked_text', 'r', encoding="utf-8-sig") as f:
                text_data = json.load(f)
            make_text_preview(user_id, text_data)

            context_text= {  # 편집 기능을 위해 미리 데이터를 render 해놓는다.
            'title' : text_data[4]['title'],
            'x_axis' : text_data[4]['detail_info']['x'],
            'y_axis' : text_data[4]['detail_info']['y'],
            'w_axis' : text_data[4]['detail_info']['width'],
            'h_axis' : text_data[4]['detail_info']['height'],
            'play_speed' : text_data[4]['detail_info']['play_speed'],
            'play_count' : text_data[4]['detail_info']['play_count'],
            'font_size' : text_data[4]['detail_info']['font_size'],
            'play_second' : text_data[4]['detail_info']['play_second'],
            "scroll_fix": text_data[4]['detail_info']['scroll_fix'],
            "font_name": "NanumGothic",
            "thickness_italics": text_data[4]['detail_info']['thickness_italics'],
            }

        #context_text = json.dumps(prev_text_info)
            len_t = int(selected_text_name[14])
            request.session['name' + str(text_index)] = selected_text_name[14 + 1 + len_t:]
            request.session['title' + str(text_index)] = text_data[4]['title']
            request.session['x_axis' + str(text_index)] = text_data[4]['detail_info']['x']
            request.session['y_axis' + str(text_index)] = text_data[4]['detail_info']['y']
            request.session['w_axis' + str(text_index)] = text_data[4]['detail_info']['width']
            request.session['h_axis' + str(text_index)] = text_data[4]['detail_info']['height']
            request.session['font_size' + str(text_index)] = text_data[4]['detail_info']['font_size']
            request.session['scroll_fix' + str(text_index)] = text_data[4]['detail_info']['scroll_fix']
            request.session['play_speed' + str(text_index)] = text_data[4]['detail_info']['play_speed']
            request.session['play_count' + str(text_index)] = text_data[4]['detail_info']['play_count']
            return render(request, 'image.html')
        else:
            print("ajax 통신 실패!")
            return redirect('image.html')
    else:
        print("POST 호출 실패!")
        return redirect('image.html')
