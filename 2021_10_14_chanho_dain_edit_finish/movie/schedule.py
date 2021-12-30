from datetime import datetime, timedelta
import calendar


def diff_date(start, end, checkdate):
    weekofday = []
    start = datetime.strptime(start, "%Y%m%d")
    end = datetime.strptime(end, "%Y%m%d")
    dates = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end - start).days + 1)]
    for i in range(len(dates)):
        year = dates[i][0:4]
        year = int(year)

        month = dates[i][4:6]
        month = int(month)

        day = dates[i][6:]
        day = int(day)

        if (checkdate[calendar.weekday(year, month, day)] == '1'):
            weekofday.append(dates[i])

    print(weekofday)

    return weekofday
