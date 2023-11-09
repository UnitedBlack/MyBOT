from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import time, logging, telebot
from random import randint
from telebot import types


TOKEN = "6604373063:AAFhU6TKDyHnHrF2Bey-hiuJ94Yv1Fct7Vw"
bot = telebot.TeleBot(TOKEN)
# logging.basicConfig(level=logging.DEBUG)
time_h = int(datetime.now().strftime("%H"))


def post_job(post, chat_id="-1002041578470"):
    media = [types.InputMediaPhoto(url, parse_mode="HTML") for url in post["post_pic"]]
    media[0].caption = post["post_text"]
    bot.send_media_group(chat_id=chat_id, media=media)
    # logging.debug(f"Posted at {time.time}")


def get_delayed_posts(scheduler):
    jobs = []
    jobs_list = scheduler.get_jobs()

    for job in jobs_list:
        run_time = job.next_run_time
        job_time = datetime.strptime(str(run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
            "%d-%m %H:%M"
        )
        data = {"jobname": job.name, "jobtime": job_time, "job_id": job.id}
        jobs.append(data)
    # logging.debug("Returning delayed posts")
    print(jobs)
    return jobs


def remove_job(data, scheduler):
    job_id = data["job_id"]
    scheduler.remove_job(job_id)
    logging.debug(f"Removed job by id {job_id}")


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
            day=custom_day, month=custom_month, hour=custom_hour, minute=custom_minute
        ),
    )
    logging.debug(f"Rescheduled to time {custom_hour}:{custom_minute}")


def schedule_post(data, scheduler):
    task_name = (
        data["post_text"]
        .splitlines()[0]
        .replace("🎁", "")
        .replace("<b>", "")
        .replace("</b>", "")
        .strip()
    )
    global time_h
    time_h = (time_h + 1) % 24
    random_minute = randint(1, 15)

    scheduler.add_job(
        post_job,
        CronTrigger(hour=time_h, minute=random_minute),
        args=[data],
        name=task_name,
    )
    # logging.debug(f"Scheduled at time {time_h}:{random_minute}")
