from datetime import datetime
allowed_hours = [hour for hour in range(10,23)]
allowed_hours = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
time_h = int(datetime.now().strftime("%H"))

time_h = allowed_hours[0] if time_h not in allowed_hours else time_h
print(time_h)

# def get_time(time_h):
# for hours in allowed_hours:
# time_h = (time_h + 1) % 24
# if time_h not in allowed_hours:
#     time_h = allowed_hours[0]
# print(time_h)
# return time_h
# current_hour = datetime.now().hour
# if not allowed_hours:
#     allowed_hours = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

# next_allowed_hour = next(
#     (hour for hour in allowed_hours if hour > current_hour),
#     allowed_hours.pop(0),
# )

# return next_allowed_hour

#     if not self.allowed_hours:
#         self.allowed_hours = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

#     next_allowed_hour = next(
#         (hour for hour in self.allowed_hours if hour > current_hour),
#         self.allowed_hours.pop(0),
#     )


# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
# print(get_time(gl_time_h))
