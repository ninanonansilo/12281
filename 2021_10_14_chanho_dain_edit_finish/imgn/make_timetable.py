from settings.update_json import time_now
import datetime
import time
import os

def make_Timetable_text():
    first_time = time.time() + 25  # play video
    second_time = time.time() + 30  # stop video
    third_time = time.time() + 31  # play image
    fourth_time = time.time() + 40  # stop image
    fifth_time = time.time() + 41  # play string
    sixth_time = time.time() + 50  # stop string
    seventh_time = time.time() + 51  # play something forever

    first_time_year = time.localtime(first_time).tm_year;
    first_time_month = time.localtime(first_time).tm_mon;
    first_time_day = time.localtime(first_time).tm_mday;
    first_time_hour = time.localtime(first_time).tm_hour;
    first_time_minute = time.localtime(first_time).tm_min;
    first_time_second = time.localtime(first_time).tm_sec;

    second_time_year = time.localtime(second_time).tm_year;
    second_time_month = time.localtime(second_time).tm_mon;
    second_time_day = time.localtime(second_time).tm_mday;
    second_time_hour = time.localtime(second_time).tm_hour;
    second_time_minute = time.localtime(second_time).tm_min;
    second_time_second = time.localtime(second_time).tm_sec;

    third_time_year = time.localtime(third_time).tm_year;
    third_time_month = time.localtime(third_time).tm_mon;
    third_time_day = time.localtime(third_time).tm_mday;
    third_time_hour = time.localtime(third_time).tm_hour;
    third_time_minute = time.localtime(third_time).tm_min;
    third_time_second = time.localtime(third_time).tm_sec;

    fourth_time_year = time.localtime(fourth_time).tm_year;
    fourth_time_month = time.localtime(fourth_time).tm_mon;
    fourth_time_day = time.localtime(fourth_time).tm_mday;
    fourth_time_hour = time.localtime(fourth_time).tm_hour;
    fourth_time_minute = time.localtime(fourth_time).tm_min;
    fourth_time_second = time.localtime(fourth_time).tm_sec;

    fifth_time_year = time.localtime(fifth_time).tm_year;
    fifth_time_month = time.localtime(fifth_time).tm_mon;
    fifth_time_day = time.localtime(fifth_time).tm_mday;
    fifth_time_hour = time.localtime(fifth_time).tm_hour;
    fifth_time_minute = time.localtime(fifth_time).tm_min;
    fifth_time_second = time.localtime(fifth_time).tm_sec;

    sixth_time_year = time.localtime(sixth_time).tm_year;
    sixth_time_month = time.localtime(sixth_time).tm_mon;
    sixth_time_day = time.localtime(sixth_time).tm_mday;
    sixth_time_hour = time.localtime(sixth_time).tm_hour;
    sixth_time_minute = time.localtime(sixth_time).tm_min;
    sixth_time_second = time.localtime(sixth_time).tm_sec;

    seventh_time_year = time.localtime(seventh_time).tm_year;
    seventh_time_month = time.localtime(seventh_time).tm_mon;
    seventh_time_day = time.localtime(seventh_time).tm_mday;
    seventh_time_hour = time.localtime(seventh_time).tm_hour;
    seventh_time_minute = time.localtime(seventh_time).tm_min;
    seventh_time_second = time.localtime(seventh_time).tm_sec;

    data = []
    info = {}
    info["time"] = {}
    info["time"]["year"] = "9999"
    info["time"]["month"] = str(first_time_month);
    info["time"]["day"] = str(first_time_day);
    info["time"]["hour"] = str(first_time_hour);
    info["time"]["minute"] = str(first_time_minute);
    info["time"]["second"] = str(first_time_second);
    info["type"] = "video";
    info["action"] = "play";
    info["title"] = ["candle.avi"];
    data.append(info)

    info = {}
    info["time"] = {}
    info["time"]["year"] = "9999"
    info["time"]["month"] = str(second_time_month);
    info["time"]["day"] = str(second_time_day);
    info["time"]["hour"] = str(second_time_hour);
    info["time"]["minute"] = str(second_time_minute);
    info["time"]["second"] = str(second_time_second);
    info["type"] = "video";
    info["action"] = "stop";
    data.append(info)

    info = {}
    info["time"] = {}
    info["time"]["year"] = "9999"
    info["time"]["month"] = str(third_time_month);
    info["time"]["day"] = str(third_time_day);
    info["time"]["hour"] = str(third_time_hour);
    info["time"]["minute"] = str(third_time_minute);
    info["time"]["second"] = str(third_time_second);
    info["type"] = "image";
    info["action"] = "play";
    info["title"] = "pikachu.jpg";
    data.append(info)

    info = {}
    info["time"] = {}
    info["time"]["year"] = "9999"
    info["time"]["month"] = str(fourth_time_month);
    info["time"]["day"] = str(fourth_time_day);
    info["time"]["hour"] = str(fourth_time_hour);
    info["time"]["minute"] = str(fourth_time_minute);
    info["time"]["second"] = str(fourth_time_second);
    info["type"] = "image";
    info["action"] = "stop";
    data.append(info)

    info = {}
    info["time"] = {}
    info["time"]["year"] = "9999"
    info["time"]["month"] = str(fifth_time_month);
    info["time"]["day"] = str(fifth_time_day);
    info["time"]["hour"] = str(fifth_time_hour);
    info["time"]["minute"] = str(fifth_time_minute);
    info["time"]["second"] = str(fifth_time_second);
    info["type"] = "string";
    info["action"] = "play";
    info["title"] = "더 나은 내일이 아니라 최악의 내일을 피하기 위해 사는걸지도 모른다.";
    info["detail_info"] = {}
    info["detail_info"]["x"] = "0";
    info["detail_info"]["y"] = "0";
    info["detail_info"]["width"] = "80";
    info["detail_info"]["height"] = "64";
    info["detail_info"]["scroll_fix"] = "0";
    info["detail_info"]["play_speed"] = "3";
    info["detail_info"]["play_count"] = "100000";
    info["detail_info"]["font_name"] = "NanumGothic";
    info["detail_info"]["font_size"] = "64";
    info["detail_info"]["play_second"] = "0";
    info["detail_info"]["thickness_italics"] = "0";
    info["detail_info"]["red_green_blue"] = "(0,255, 239)"
    data.append(info)

    info = {}
    info["time"] = {}
    info["time"]["year"] = "9999"
    info["time"]["month"] = str(sixth_time_month);
    info["time"]["day"] = str(sixth_time_day);
    info["time"]["hour"] = str(sixth_time_hour);
    info["time"]["minute"] = str(sixth_time_minute);
    info["time"]["second"] = str(sixth_time_second);
    info["type"] = "string";
    info["action"] = "stop";
    data.append(info)


    return data





