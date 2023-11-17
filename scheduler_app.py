import telebot
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from datetime import datetime
from telebot import types
from random import randint
from configure_bot import TOKEN

bot = telebot.TeleBot(TOKEN)
time_h = int(datetime.now().strftime("%H"))
days_delta = 0
last_hour = None
last_day = None
last_month = None


def post_job(post):
    chat_id = post["chat_id"]
    media = [types.InputMediaPhoto(url, parse_mode="HTML") for url in post["post_pic"]]
    media[0].caption = post["post_text"]
    bot.send_media_group(chat_id=chat_id, media=media)


def schedule_post(data, scheduler, ad=False):
    global last_hour, last_day, last_month
    global time_h, days_delta
    task_name = (
        data["post_text"]
        .splitlines()[0]
        .replace("🎁", "")
        .replace("<b>", "")
        .replace("</b>", "")
        .strip()
    )
    if ad:
        task_name = "*РЕКЛАМА*" + task_name

    random_minute = randint(1, 20)

    time_h = last_hour if last_hour else (time_h + 1) % 24
    days_delta = last_day - datetime.now().day if last_day else days_delta
    if time_h < 10 or time_h > 22:
        time_h = 10
        now = datetime.now()
        scheduled_time = now.replace(hour=time_h, minute=random_minute)
        days_delta += 1
    else:
        now = datetime.now()
        scheduled_time = now.replace(hour=time_h, minute=random_minute)
        
    scheduled_time += timedelta(days_delta)
    day = scheduled_time.day
    month = last_month if last_month else scheduled_time.month
    minute = scheduled_time.minute
    year = scheduled_time.year

    scheduler.add_job(
        post_job,
        CronTrigger(day=day, hour=time_h, minute=minute, month=month, year=year),
        args=[data],
        name=task_name,
    )
    last_hour = False
    last_day = False
    last_month = False


def get_delayed_posts(scheduler):
    global last_hour, last_day, last_month
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
    if jobs_list and last_hour is None and last_day is None and last_month is None:
        last_run_time = jobs_list[-1].next_run_time
        last_hour = int(datetime.strptime(
            str(last_run_time), "%Y-%m-%d %H:%M:%S%z"
        ).strftime("%H")) + 1
        last_day = int(datetime.strptime(
            str(last_run_time), "%Y-%m-%d %H:%M:%S%z"
        ).strftime("%d"))
        last_month = int(datetime.strptime(
            str(last_run_time), "%Y-%m-%d %H:%M:%S%z"
        ).strftime("%m"))

    return jobs


def delete_job(job_id, scheduler):
    scheduler.remove_job(job_id)


def reschedule_post(data, scheduler):
    jobs_list = scheduler.get_jobs()
    for job in jobs_list:
        print(job.id)

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
