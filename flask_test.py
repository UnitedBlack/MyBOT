from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telebot import types
import time, logging, telebot

app = Flask(__name__)

TOKEN = "6604373063:AAFhU6TKDyHnHrF2Bey-hiuJ94Yv1Fct7Vw"
bot = telebot.TeleBot(TOKEN)
# logging.basicConfig(level=logging.DEBUG)
time_h = int(datetime.now().strftime("%H"))


def post_job(post):
    media = [types.InputMediaPhoto(url, parse_mode="HTML") for url in post["post_pic"]]
    media[0].caption = post["post_text"]
    bot.send_media_group(chat_id="-1002041578470", media=media)
    logging.debug(f"Posted at {time.time}")


def get_delayed_posts():
    jobs = []
    jobs_list = scheduler.get_jobs()

    for job in jobs_list:
        run_time = job.next_run_time
        job_time = datetime.strptime(str(run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
            "%d-%m %H:%M"
        )
        data = {"jobname": job.name, "jobtime": job_time, "job_id": job.id}
        jobs.append(data)
    print(jobs)
    return jobs
# data = {"get_delayed_posts": "get_delayed_posts"}

def remove_job(data):
    job_id = data["job_id"]
    scheduler.remove_job(job_id)
    print("Removed")
# data = {"job_id": "14234234"}

def reschedule_post(data):
    job_id = data["job_id"]
    custom_day = data["custom_day"]
    custom_hour = data["custom_hour"]
    scheduler.reschedule_job(job_id, CronTrigger(day=custom_day, hour=custom_hour))
    print("Added custom time")
# data = {"custom_hour": "5", "custom_day": "1", "job_id": "12431"}


def schedule_post(data):
    task_name = (
        data["post_text"]
        .splitlines()[0]
        .replace("🎁", "")
        .replace("<b>", "")
        .replace("</b>", "")
        .strip()
    )
    global time_h
    time_h = time_h + 1 % 24

    scheduler.add_job(
        post_job, CronTrigger(hour=time_h), args=[data], name=task_name
    )
    print("scheduled")


@app.route("/", methods=["GET"])
def root():
    return "Hello, World!", 200


@app.route("/", methods=["POST"])
def receive_message_at_root():
    message = request.get_json()

    if message.get("custom_time"):
        print("reschedule")
        reschedule_post(message)
        return jsonify({"status": "Posted with custom time"}), 200

    elif message.get("post_text"):
        schedule_post(message)
        print("text")
        return jsonify({"status": "Posted"}), 200

    elif message.get("job_id"):
        remove_job(message)
        print("id")
        return jsonify({"status": "Job deleted"}), 200

    elif message.get("get_delayed_posts"):
        print("delay")
        posts = get_delayed_posts()
        return jsonify({"delayed_posts": posts}), 200

    else:
        return jsonify({"status": "Didn't understand you"}), 500


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.daemonic = False
    scheduler.start()
    app.run(host="0.0.0.0", port=80, debug=False)