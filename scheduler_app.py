import telebot
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from datetime import datetime
from telebot import types
from random import randint
from configure_bot import TOKEN
from apscheduler.schedulers.background import BackgroundScheduler
from configure_bot import jobstores_tp
import calendar

bot = telebot.TeleBot(TOKEN)
time_h = int(datetime.now().strftime("%H"))


def post_job(post):
    chat_id = post["chat_id"]
    media = [types.InputMediaPhoto(url, parse_mode="HTML") for url in post["post_pic"]]
    media[0].caption = post["post_text"]
    bot.send_media_group(chat_id=chat_id, media=media)


def schedule_post(data, scheduler, ad=False, custom_time=False):
    task_name = (
        data["post_text"]
        .splitlines()[0]
        .replace("🎁", "")
        .replace("<b>", "")
        .replace("</b>", "")
        .strip()
    )
    task_name = "*РЕКЛАМА*" + task_name if ad else task_name
    # random_minute = randint(1, 20)
    if custom_time:
        hour, minute, day, month, year = custom_time
    else:
        day, month, year, hour, minute = get_free_time(scheduler)
    print(day, hour)
    scheduler.add_job(
        post_job,
        CronTrigger(day=day, hour=hour, minute=minute, month=month, year=year),
        args=[data],
        name=task_name,
    )


def get_free_time(scheduler, get_allowed=False):
    jobs = scheduler.get_jobs()
    current_day = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_hour = datetime.now().hour
    minute = 0
    allowed_hours_dict = {}
    if current_hour >= 22 or current_hour < 10:
        current_day += 1
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    for day in range(current_day, days_in_month + 1):
        allowed_hours = set(range(10, 23))
        for job in jobs:
            run_time = job.next_run_time
            if (
                run_time
                and run_time.day == day
                and run_time.month == current_month
                and run_time.year == current_year
            ):
                hour_job_time = int(
                    datetime.strptime(str(run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
                        "%H"
                    )
                )
                allowed_hours.discard(hour_job_time)
        allowed_hours_dict[day] = list(allowed_hours)
    if get_allowed:
        return current_day, current_month, current_year, allowed_hours_dict
    else:
        return (
            current_day,
            current_month,
            current_year,
            min(allowed_hours_dict[current_day]),
            minute
        )


def get_delayed_posts(scheduler):
    jobs = []
    jobs_list = scheduler.get_jobs()
    jobs_list = [job for job in jobs_list if job.next_run_time is not None]
    jobs_list.sort(key=lambda job: job.next_run_time)

    for job in jobs_list:
        run_time = job.next_run_time
        job_time = datetime.strptime(str(run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
            "%d-%m %H:%M"
        )
        data = {"jobname": job.name, "jobtime": job_time, "job_id": job.id}
        jobs.append(data)
    return jobs


def delete_job(job_id, scheduler):
    scheduler.remove_job(job_id)


def reschedule_post(data, scheduler):
    user_job_id = data["job_id"]
    custom_hour = data["custom_hour"]
    custom_minute = data["custom_minute"]
    custom_day = data["custom_day"]
    custom_month = data["custom_month"]
    scheduler.reschedule_job(
        job_id=user_job_id,
        trigger=CronTrigger(
            day=custom_day,
            month=custom_month,
            hour=custom_hour,
            minute=custom_minute,
        ),
    )
    # logging.debug(f"Rescheduled to time {custom_hour}:{custom_minute}")


def remove_all_jobs(scheduler):
    global time_h, day
    time_h = 10
    day = datetime.now().day
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.remove_job(job.id)


# if __name__ == "__main__":
#     schedulerTP = BackgroundScheduler(jobstores=jobstores_tp)
#     schedulerTP.start()
#     print(get_free_time(scheduler=schedulerTP))
# if jobs_list and last_hour is None and last_day is None and last_month is None:
#     ad_post = [job.name.startswith("*РЕКЛАМА*") for job in jobs]
#     print(ad_post)
#     last_run_time = jobs_list[-1].next_run_time
#     last_hour = (
#         int(
#             datetime.strptime(str(last_run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
#                 "%H"
#             )
#         )
#         + 1
#     )
#     last_day = int(
#         datetime.strptime(str(last_run_time), "%Y-%m-%d %H:%M:%S%z").strftime("%d")
#     )
#     last_month = int(
#         datetime.strptime(str(last_run_time), "%Y-%m-%d %H:%M:%S%z").strftime("%m")
#     )
#     time_h = last_hour if last_hour else (time_h + 1) % 24
#     days_delta = last_day - datetime.now().day if last_day else days_delta
#     if time_h < 10 or time_h > 22:
#         time_h = 10
#         now = datetime.now()
#         scheduled_time = now.replace(hour=time_h, minute=random_minute)
#         days_delta += 1
#     else:
#         now = datetime.now()
#         scheduled_time = now.replace(hour=time_h, minute=random_minute)

#     scheduled_time += timedelta(days_delta)
#     day = scheduled_time.day
#     month = last_month if last_month else scheduled_time.month
#     minute = scheduled_time.minute
#     year = scheduled_time.year`

# def get_free_time(scheduler):
#     jobs = scheduler.get_jobs()
#     allowed_hours = set(range(10, 23))
#     current_day = datetime.now().day
#     current_month = datetime.now().month
#     current_year = datetime.now().year
#     current_hour = datetime.now().hour
#     if current_hour >= 22 or current_hour < 10:
#         current_day += 1
#     while True:
#         for job in jobs:
#             run_time = job.next_run_time
#             if (
#                 run_time
#                 and run_time.day == current_day
#                 and run_time.month == current_month
#                 and run_time.year == current_year
#             ):
#                 hour_job_time = int(
#                     datetime.strptime(str(run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
#                         "%H"
#                     )
#                 )
#                 allowed_hours.discard(hour_job_time)

#         if allowed_hours:
#             return current_day, current_month, current_year, min(allowed_hours)
#         else:
#             current_day += 1
#             if current_day > calendar.monthrange(current_year, current_month)[1]:
#                 current_day = 1
#                 current_month += 1
#                 if current_month > 12:
#                     current_month = 1
#                     current_year += 1
#             allowed_hours = set(range(10, 23))
