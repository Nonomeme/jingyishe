# Create your tests here.

import datetime,pytz

time1 = datetime.date.today()

time2 = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))

print time1
print time2

print time1.day == time2.day
