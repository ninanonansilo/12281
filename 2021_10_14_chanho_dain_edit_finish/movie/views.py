from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from settings.update_json import *
from imgn.media_json import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from movie.schedule import *
from django.contrib.auth.models import User

from register.models import Profile
from os.path import getsize
from django.contrib import messages

# Create your views here.


@csrf_exempt
def movie(request):
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

        print("sdf[efjfh9ejfh")
        print(user_id)
        createDirectory(user_id)
        file_list = os.listdir(user_id)
        check_index = -1
        for i in range(len(file_list)):
            if (len(file_list[i]) < 3):
                check_index = int(file_list[i])


        print("movie 호출 직후 = {}".format(userinfo.profile.var_check_index))
        play_list = directory_list(user_id) # 재생목록 이름 리스트 (고유번호 포함)
        list_name = []
        list_date = []
        list_schedule = []
        list_overlap = 0
        print(play_list)
        for i in range(len(play_list)):
            list_date.append(play_list[i][0:4] + '-' + play_list[i][4:6] + '-' + play_list[i][6:8] + ' (' + play_list[i][8:10] +':' +
                            play_list[i][10:12] +')') # 앞에 14자리 - 등록일
            list_name.append(play_list[i][14:])

        print("현재 등록된 재생목록->")
        print(list_name)

        list_index = check_index

        print("movie 호출 후 list_index 변경 = {}".format(list_index))
        media_list = []
        if (list_index != -1): # 체크된 상태라면 -> 해당 재생목록의 동영상들을 가져오기
            if list_index >= len(play_list):
                pass
            else:
                param_play_list_name = play_list[list_index] # 선택한 재생목록 이름 (고유번호 포함)
                media_list = video_list_in_bucket(user_id, param_play_list_name) # 고유번호 14자리를 제외한 동영상 이름
                schedule_list = schedule_list_in_bucket(user_id, param_play_list_name, -2) # 재생일정 리스트 (각 , 38자리 / 초기는 14자리)

                list_overlap = check_overlap(schedule_list_in_bucket(user_id, param_play_list_name, -2))


                # 쪼개서 UI에 표시할 문자열로 저장 (append) , 14자리(일정 미설정) => 조건 처리하여 '미설정' 표시
                for i in range(len(schedule_list)):
                    if (len(schedule_list[i]) == 14): #  재생일정 미등록
                        list_schedule.append("미등록")
                    else:
                        list_schedule.append("(" + schedule_list[i][16:18] + "." + schedule_list[i][18:20] + "." + schedule_list[i][20:22] + "~" +
                                            schedule_list[i][24:26] + "." + schedule_list[i][26:28] + "." +schedule_list[i][28:30] + ")"
                                            + schedule_list[i][30:32] + ":" + schedule_list[i][32:34] + "~" + schedule_list[i][34:36] + ":" + schedule_list[i][36:38])


        list_dict = {
            'list_name': list_name,  # 재생목록 -> 이름
            'list_date': list_date,  # 재생목록 -> 등록일
            'list_index': list_index,  # 체크 -> 인덱스
            'list_media': media_list,  # 선택된 재생목록 내 동영상
            'list_schedule' : list_schedule, # 재생일정 표시
            'list_overlap' : list_overlap, #시간중복확인
            'list_videoindex' : userinfo.profile.var_move_movie_index,  #비디오 위아래 이동시 인덱스
            }

        print("재생목록 내 동영상 리스트->")
        print(media_list)

        context = json.dumps(list_dict)
        return render(request, 'mov.html', {'context': context, 'userinfo':userinfo, 'user_id': user_id})


@csrf_exempt
def downmove_movie(request):
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            video_index = int(request.POST['video_index'])
            play_list_index = int(request.POST['play_list_index'])

            play_list = directory_list(user_id)
            if (play_list_index >= len(play_list)):
                pass
            else:
                play_list_name = play_list[play_list_index]  # 지울 동영상이 속해있는 재생목록 이름 (고유번호 포함)
                video_name_list = video_list_in_bucket_include_code(user_id, play_list_name)

                thisvideo_serial = video_name_list[video_index][:14]
                thisvideo_name =  video_name_list[video_index][14:]
                userinfo = User.objects.get(username=request.user.username)
                userinfo.profile.var_move_movie_index = video_index + 1

                nextvideo_serial = video_name_list[video_index+1][:14]
                nextvideo_name = video_name_list[video_index+ 1][14:]

                change_thisvideo = nextvideo_serial + thisvideo_name
                change_nextvideo = thisvideo_serial+nextvideo_name

                rename_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name + "/"+video_name_list[video_index],
                           user_id + "/PLAY_LIST/" + play_list_name +"/"+ change_thisvideo)
                rename_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name + "/" + video_name_list[video_index+1],
                            user_id + "/PLAY_LIST/" + play_list_name + "/" + change_nextvideo)

                param_play_list_name = play_list[play_list_index]  # 선택한 재생목록 이름 (고유번호 포함)

                schedule_list = schedule_list_in_bucket(user_id, param_play_list_name, -2)  # 재생일정 리스트 (각 , 38자리 / 초기는 14자리)
                thisvideo_schedule = schedule_list[video_index]
                nextvideo_schedule = schedule_list[video_index+1]
                if(len(thisvideo_schedule) == 14):
                    if(len(nextvideo_schedule) == 14):
                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        nextvideo_schedule_makedate = nextvideo_schedule[:14]

                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule_makedate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule_makedate + "temp")
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule_makedate + "temp",
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate)
                    else:

                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        nextvideo_schedule_makedate = nextvideo_schedule[:14]
                        nextvideo_schedule_playdate = nextvideo_schedule[14:]

                        delete_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule)
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule_makedate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule + "temp")
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule + "temp",
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate + nextvideo_schedule_playdate)
                else:
                    if (len(nextvideo_schedule) == 14):
                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        thisvideo_schedule_playdate = thisvideo_schedule[14:]
                        nextvideo_schedule_makedate = nextvideo_schedule[:14]
                        delete_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule)
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule + "temp")
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule + "temp",
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule+thisvideo_schedule_playdate)

                    else:
                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        thisvideo_schedule_playdate = thisvideo_schedule[14:]
                        nextvideo_schedule_makedate = nextvideo_schedule[:14]

                        nextvideo_schedule_playdate = nextvideo_schedule[14:]
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule_makedate + thisvideo_schedule_playdate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule + "temp")
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule + "temp",
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate + nextvideo_schedule_playdate)
                        delete_blob(using_bucket, user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + nextvideo_schedule)
                #thisvideo_schedule_date

            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')
@csrf_exempt
def upmove_movie(request):
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            video_index = int(request.POST['video_index'])
            play_list_index = int(request.POST['play_list_index'])

            play_list = directory_list(user_id)
            if (play_list_index >= len(play_list)):
                pass
            else:
                play_list_name = play_list[play_list_index]  # 지울 동영상이 속해있는 재생목록 이름 (고유번호 포함)
                video_name_list = video_list_in_bucket_include_code(user_id, play_list_name)

                thisvideo_serial = video_name_list[video_index][:14]
                thisvideo_name =  video_name_list[video_index][14:]
                userinfo = User.objects.get(username=request.user.username)

                userinfo.profile.var_move_movie_index = video_index - 1

                prevideo_serial = video_name_list[video_index-1][:14]
                prevideo_name = video_name_list[video_index- 1][14:]

                change_thisvideo = prevideo_serial + thisvideo_name
                change_prevideo = thisvideo_serial+prevideo_name


                rename_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name + "/"+video_name_list[video_index],
                           user_id + "/PLAY_LIST/" + play_list_name +"/"+ change_thisvideo)
                rename_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name + "/" + video_name_list[video_index-1],
                            user_id + "/PLAY_LIST/" + play_list_name + "/" + change_prevideo)

                param_play_list_name = play_list[play_list_index]  # 선택한 재생목록 이름 (고유번호 포함)

                schedule_list = schedule_list_in_bucket(user_id, param_play_list_name, -2)  # 재생일정 리스트 (각 , 38자리 / 초기는 14자리)
                thisvideo_schedule = schedule_list[video_index]
                prevideo_schedule = schedule_list[video_index - 1]
                if (len(thisvideo_schedule) == 14):
                    if (len(prevideo_schedule) == 14):
                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        prevideo_schedule_makedate = prevideo_schedule[:14]

                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule_makedate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule_makedate + "temp")
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule_makedate + "temp",
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate)
                    else:


                        thivideo_schedule_makedate = thisvideo_schedule[:14]
                        thisvideo_schedule_playdate = thisvideo_schedule[14:]
                        prevideo_schedule_makedate = prevideo_schedule[:14]
                        prevideo_schedule_playdate = prevideo_schedule[14:]

                        delete_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule)
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thivideo_schedule_makedate + prevideo_schedule_playdate )
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule_makedate)

                else:
                    if (len(prevideo_schedule) == 14):
                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        thisvideo_schedule_playdate = thisvideo_schedule[14:]
                        prevideo_schedule_makedate = prevideo_schedule[:14]
                        prevideo_schedule_playdate = prevideo_schedule[14:]
                        delete_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule)
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + prevideo_schedule_makedate + thisvideo_schedule_playdate)


                    else:
                        thisvideo_schedule_makedate = thisvideo_schedule[:14]
                        thisvideo_schedule_playdate = thisvideo_schedule[14:]
                        prevideo_schedule_makedate =  prevideo_schedule[:14]
                        prevideo_schedule_playdate =  prevideo_schedule[14:]
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" +  prevideo_schedule_makedate + thisvideo_schedule_playdate)
                        UPLOAD(using_bucket, 'test',
                               user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" +  prevideo_schedule + "temp")
                        rename_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" +  prevideo_schedule + "temp",
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + thisvideo_schedule_makedate +  prevideo_schedule_playdate)
                        delete_blob(using_bucket,
                                    user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" +  prevideo_schedule)
                # thisvideo_schedule_date


            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')


@csrf_exempt
def video_list(request):
    userinfo = User.objects.get(username=request.user.username)
    user_id = userinfo.profile.player_serial

    temp = request.POST['index']

    print("video_list 변경전 = {}".format(temp))
    #userinfo = User.objects.get(username=request.user.username)
    #userinfo.profile.var_check_index = temp

    createDirectory(user_id)
    flag = 0 # 플래그
    over_file = []
    file_list = os.listdir(user_id)
    print(file_list)
    for i in range(len(file_list)):
        if (len(file_list[i]) < 3):
            os.rename(user_id + "/" + file_list[i], user_id + "/" + temp) # 변수파일 이름 사용할 이름으로 변경
            flag = flag + 1 # 플래그가 0이면 변수파일이 없는 거임 만들어야함
            over_file.append(file_list[i])
    if flag > 1: # 2개 이상있으면 삭제
        for j in range(flag):
            os.remove(user_id + "/" + over_file[j])
    if flag == 0: # 기존에 없었으면 새로 생성
        f = open(user_id + "/"+ str(temp), 'w')
        f.close()


    return render(request, 'mov.html')
    #return redirect('movie.html')


@csrf_exempt
def upload_list(request):  # 재생목록 추가 ( GCP에 해당하는 이름의 디렉토리를 만듬)
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            print(request.POST['list'])    # 리스트 이름
            input = request.POST['list']
            list_name = input # 임시방편
            list_name = list_name.replace("/","-")
            # -- 업로드 , 이런식으로 하면 오류 없이 디렉토리 생성가능
            now_kst = time_now()  # 현재시간 받아옴
            UPLOAD(using_bucket, 'test' , user_id + "/PLAY_LIST/" + now_kst.strftime("%Y%m%d%H%M%S") + str(list_name) + "/")
            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')


def directory_list(user_id):   # 디렉토리가 '/'로 끝나는 특징을 사용해 디렉토리 이름만 추출

    play_list_name = play_list_in_bucket(user_id)  # 중복 확인을 위해 PLAY_LIST 하위 이름들의 배열)
    list_name = []
    for i in range(len(play_list_name)):
        if play_list_name[i][-1:] == '/':
            list_name.append(play_list_name[i][:-1])
    return list_name


@csrf_exempt
def upload_video(request):  # 재생목록에 동영상 업로드
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            video_name = request.POST['video_name']  # 동영상 이름
            play_list_index = int(request.POST['list_name']) # 재생목록 인덱스

            if (play_list_index == -1):  # 재생목록이 선택되지 않은 상태라면 저장하지 않음
                return redirect('movie.html')
            video = request.FILES.get('video')  # 동영상을 request에서 받아옴

            path = default_storage.save(user_id + "/video", ContentFile(video.read()))

            play_list = directory_list(user_id)
            checked_play_list = play_list[play_list_index]
            now_kst = time_now()  # 현재시간 받아옴


            UPLOAD(using_bucket, user_id + "/video",user_id + "/PLAY_LIST/" + checked_play_list + now_kst.strftime("/%Y%m%d%H%M%S") + video_name)
            UPLOAD(using_bucket, "test" ,user_id + "/VIDEO_SCHEDULE/" + checked_play_list + now_kst.strftime("/%Y%m%d%H%M%S"))

            os.remove(user_id + "/video")  # 장고에서 중복된 이름의 파일에는 임의로 이름을 변경하기 때문에 임시파일은 제거
            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')


@csrf_exempt
def delete_play_list(request):  # 선택된 재생목록 삭제
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            delete_index = int(request.POST['play_list_index'])
            play_list = directory_list(user_id)
            if (delete_index >= len(play_list)):
                pass
            else:
                delete_name = play_list[delete_index]
                timetable_list = timetable_list_in_bucket(user_id)
                if (delete_name == timetable_list[-1][14:]): # 최근 타임테이블(현재 재생중)이 지금 삭제되었다면 전광판에도 정지
                    blank = []
                    save_file(user_id, blank)
                    now_kst = time_now()
                    UPLOAD(using_bucket, user_id + "/send",user_id + "/JSON/TIMETABLE/" + now_kst.strftime("%Y%m%d%H%M%S")) # 비어있는 타임테이블 업로드
                delete_video_list = video_list_in_bucket_include_code(user_id, delete_name)  # 하위 객체들을 먼저 지우기 위함
                print('delete_video_list --> {}'.format(delete_video_list))
                delete_schedule_list = schedule_list_in_bucket(user_id, delete_name, -2)
                print('delete_schedule_list --> {}'.format(delete_schedule_list))
                for i in range(len(delete_video_list)):
                    delete_blob(using_bucket, user_id + "/PLAY_LIST/" + delete_name + "/" + delete_video_list[i])
                delete_blob(using_bucket, user_id + "/PLAY_LIST/" + delete_name + "/") # 재생목록 삭제
                for i in range(len(delete_schedule_list)):
                    delete_blob(using_bucket, user_id + "/VIDEO_SCHEDULE/" + delete_name + "/" + delete_schedule_list[i])
                #delete_blob(using_bucket, user_id + "/VIDEO_SCHEDULE/" + delete_name + "/") # 스케쥴도 삭제

            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')


@csrf_exempt
def delete_video(request):  # 선택된 재생목록 삭제
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            video_index = int(request.POST['video_index'])
            play_list_index = int(request.POST['play_list_index'])

            play_list = directory_list(user_id)
            if (play_list_index >= len(play_list)):
                pass
            else:
                play_list_name = play_list[play_list_index] # 지울 동영상이 속해있는 재생목록 이름 (고유번호 포함)
                video_name_list = video_list_in_bucket_include_code(user_id, play_list_name)
                if (video_index >= len(video_name_list)): # 없는 부분의 체크박스 선택시
                    pass
                else:
                    # 동영상 삭제
                    delete_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name + "/" + video_name_list[video_index])
                    # 스케쥴도 삭제
                    delete_schedule_name = schedule_list_in_bucket(user_id, play_list_name, video_index)
                    delete_blob(using_bucket, user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + delete_schedule_name)


            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')



@csrf_exempt
def play_schedule(request):
    if request.method == 'POST':
        if is_ajax(request):

            start_day = request.POST["start_day"]
            start_day = re.sub(r'[^0-9]', '', start_day)
            finish_day = request.POST["finish_day"]
            finish_day = re.sub(r'[^0-9]', '', finish_day)
            start_hour = request.POST["start_hour"]
            finish_hour = request.POST["finish_hour"]
            start_min = request.POST["start_min"]
            finish_min = request.POST["finish_min"]
            video_index = int(request.POST["video_index"])
            play_list_index = request.POST["play_list_index"]

            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            userinfo.profile.var_sun = request.POST["sun"]
            userinfo.profile.var_mon = request.POST["mon"]
            userinfo.profile.var_tues = request.POST["tues"]
            userinfo.profile.var_wed = request.POST["wed"]
            userinfo.profile.var_thurs = request.POST["thurs"]
            userinfo.profile.var_fri = request.POST["fri"]
            userinfo.profile.var_sat = request.POST["sat"]
            print(start_day , finish_day)
            # 선택한 인덱스의 파일이름을 가져와 14자리 떼어냄
            play_list = directory_list(user_id)
            play_list_name = play_list[int(play_list_index)] # 재생목록 이름 (14자리 포함)
            video_list = video_list_in_bucket_only_code(user_id, play_list_name) # 현재 보고있는 동영상 리스트
            file_code = video_list[video_index]  # file_code => 고유번호 14자리

            if (video_index >= len(video_list)):
                pass
            else:
                # VIDEO_SCH EDULE -> 선택 파일의 현재 이름
                rename_prev = schedule_list_in_bucket(user_id, play_list_name ,video_index)

                new_name = str(file_code) + start_day + finish_day + start_hour + start_min + finish_hour + finish_min
                # VIDEO_SCHEDULE에 등록한 스케쥴로 변경
                rename_blob(using_bucket , user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + rename_prev
                            ,user_id + "/VIDEO_SCHEDULE/" + play_list_name + "/" + new_name)



            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')

@csrf_exempt


def check_overlap(input):

    length = len(input)
    clear_input = []
    for i in range(length):
        if (len(input[i]) == 38):
            input[i] = input[i][14:]
            clear_input.append(input[i])
    clear_input.sort()
    input = clear_input
    length = len(input)
    for j in range(length - 1):
        temp = input[j]
        print(temp)
        for i in range(j, length - 1):
            print(input[i + 1])
            if (input[i + 1][0:8]) <= temp[8:16]:
                if (input[i + 1][16:20] < temp[20:24]):
                    return True
                else:
                    return False
            else:

                return False



@csrf_exempt
def play_list_trans(request): # 재생목록 전송
    if request.method == 'POST':
        if is_ajax(request):
            userinfo = User.objects.get(username=request.user.username)
            user_id = userinfo.profile.player_serial

            play_list_index = int(request.POST["index"])
            now_kst = time_now()
            # 인덱스로 재생목록 이름 따 옴
            play_list = directory_list(user_id)
            play_list_name = play_list[play_list_index]
            video_name_list = video_list_in_bucket_include_code(user_id, play_list_name)  # 동영상(풀 네임) 리스트
            # 따온 재생목록 이름으로 동영상 스케쥴 폴더 -> 재생목록 이름 으로 접근
            schedule_list = schedule_list_in_bucket(user_id, play_list_name, -2)


            data = []
            auto_play_list = []
            # 해당 디렉토리의 이름들로 스케쥴 작성 , 일정 미작성 동영상(또는 과거) 모두 고려
            for i in range(len(schedule_list)): # 스케쥴 개수(재생목록 내 동영상 개수) 만큼 반복
                print(schedule_list)
                if len(schedule_list[i]) == 14:  # 최초 등록 후 일정추가를 안한 영상은 패스
                    auto_play_list.append(i)  # 미등록 영상은 따로 모음 , 인덱스만 저장
                elif len(schedule_list[i]) == 38: # 한개의 동영상
                    # 해당 동영상 PLAY_LIST -> MEDIA/video로 옮기는 작업

                    copy_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name +"/" + video_name_list[i],
                              using_bucket, user_id + "/MEDIA/video/" + video_name_list[i][14:])

                    userinfo = User.objects.get(username=request.user.username)

                    list_dayofweek = [userinfo.profile.var_mon, userinfo.profile.var_tues, userinfo.profile.var_wed,userinfo.profile.var_thurs,userinfo.profile.var_fri,
                                      userinfo.profile.var_sat,userinfo.profile.var_sun]
                    if 1 not in list_dayofweek: list_dayofweek = ['1','1','1','1','1','1','1']


                    list_date = diff_date(str(schedule_list[i][14:22]),str(schedule_list[i][22:30]), list_dayofweek) # 날짜 리스트 반환 (str)

                    for j in range(len(list_date)):
                        info = {}
                        info["time"] = {}
                        info["time"]["year"] = list_date[j][:4]
                        info["time"]["month"] = list_date[j][4:6]
                        info["time"]["day"] = list_date[j][6:8]
                        info["time"]["hour"] = schedule_list[i][30:32]
                        info["time"]["minute"] = schedule_list[i][32:34]
                        info["time"]["second"] = "01"
                        info["time"]["alltime"] = list_date[j] + schedule_list[i][30:34] + "00"
                        info["type"] = "video"
                        info["action"] = "play"
                        info["title"] = [video_name_list[i][14:]]

                        # 해당 부분은 과거 시간이 들어오면 터지는 기존 방식 때문에 과거시간을 막는 방법인데, 구현 방법이 바뀜에 따라 미사용 (과거시간 그대로 넣어달라 요청)
                        #if(((info["time"]["year"]) == now_kst.strftime("%Y").zfill(4)) and ((info["time"]["month"]) == now_kst.strftime("%m").zfill(2)) and
                        #((info["time"]["day"]) == now_kst.strftime("%d").zfill(2)))  : # 날짜가 오늘인 경우
                        #    if((int(info["time"]["alltime"])) <= int(now_kst.strftime("%Y%m%d%H%M%S"))) : # 또 그중에서 시작시간이 과거인 경우 -> 영상 시작 시간을 현재시간 + 10초 정도로 설정함
                        #        start_time = now_kst
                        #        start_time = start_time + timedelta(seconds=15)
                        #        info["time"]["hour"] = start_time.strftime("%H").zfill(2)
                        #        info["time"]["minute"] = start_time.strftime("%M").zfill(2)
                        #        info["time"]["second"] = start_time.strftime("%S").zfill(2)

                                # 우려되는 버그
                                # 1. 15초를 더했는데 날짜가 바뀌는 경우
                                # 2. 영상이 STOP되는 시간이 지금 설정한 시간보다 먼저 오는 경우우
                        data.append(info)

                        info = {}
                        info["time"] = {}
                        info["time"]["year"] = list_date[j][:4]
                        info["time"]["month"] = list_date[j][4:6]
                        info["time"]["day"] = list_date[j][6:8]
                        info["time"]["hour"] = schedule_list[i][34:36]
                        info["time"]["minute"] = schedule_list[i][36:38]
                        info["time"]["second"] = "00"
                        info["time"]["alltime"] = list_date[j] + schedule_list[i][34:38] + "00"
                        info["type"] = "video"
                        info["action"] = "stop"

                        data.append(info)
                else:
                    print("스케줄 자릿수 error")
                    pass
            if (len(auto_play_list) > 0): # 미등록 영상의 처리 ( 자동 재생 )
                auto_play_name = []
                for k in range(len(auto_play_list)):
                    index_auto = auto_play_list[k] # 자동재생 영상의 인덱스
                    auto_play_name.append(str(video_name_list[index_auto][14:]))  # 재생할 영상의 이름들

                start_time = now_kst  # 즉시 시작용 시간 계산
                start_time = start_time + timedelta(seconds=14)

                info = {}
                info["time"] = {}
                info["time"]["year"] = start_time.strftime("%Y").zfill(4)
                info["time"]["month"] = start_time.strftime("%m").zfill(2)
                info["time"]["day"] = start_time.strftime("%d").zfill(2)
                info["time"]["hour"] = start_time.strftime("%H").zfill(2)
                info["time"]["minute"] = start_time.strftime("%M").zfill(2)
                info["time"]["second"] = start_time.strftime("%S").zfill(2)
                info["time"]["alltime"] = (start_time.strftime("%Y").zfill(4) + start_time.strftime("%m").zfill(2) + start_time.strftime("%d").zfill(2) +
                                               start_time.strftime("%H").zfill(2) + start_time.strftime("%M").zfill(2) + start_time.strftime("%S").zfill(2))
                info["type"] = "video"
                info["action"] = "play"
                info["title"] = auto_play_name
                data.append(info)

                info = {}
                info["time"] = {}
                info["time"]["year"] = "9999"
                info["time"]["month"] = "01"
                info["time"]["day"] = "01"
                info["time"]["hour"] = "00"
                info["time"]["minute"] = "00"
                info["time"]["second"] = "00"
                info["time"]["alltime"] = "99990101000000"
                info["type"] = "video"
                info["action"] = "stop"
                data.append(info)
            video_names = video_list_in_bucket(user_id, play_list_name)

            for i in range(len(video_names)):  # 재생목록안 영상들 모두 업로드
                copy_blob(using_bucket, user_id + "/PLAY_LIST/" + play_list_name + "/" + video_name_list[i] ,using_bucket,
                      user_id + "/MEDIA/video/" + video_names[i])

            save_file(user_id, data)
            UPLOAD(using_bucket, user_id + "/send" ,user_id + "/JSON/TIMETABLE/" + now_kst.strftime("%Y%m%d%H%M%S") + play_list_name)

            # 타임테이블을 새로작성하여 기존 타임테이블을 다 죽임
            # 아직 파일 저장만하고 업로드는 넣지않음

            return redirect('movie.html')
        else:
            print("ajax 통신 실패!")
            return redirect('movie.html')
    else:
        print("POST 호출 실패!")
        return redirect('movie.html')
