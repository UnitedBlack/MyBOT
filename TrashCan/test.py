from datetime import datetime

time1 = "2023-10-31 01:00:00+03:00"
dt = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S%z")
print(dt.hour)
