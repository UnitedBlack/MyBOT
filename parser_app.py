from aiogram.utils.markdown import hbold, hstrikethrough, hcode, hlink
from configure_bot import GOO_SO_TOKEN, TOKEN
from datetime import datetime
import sql, tg_sql, ast, logging, json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telebot import types
import telebot
from random import randint, choice


class Scrapy:
    def __init__(
        self,
        skidka_link,
        connection_wb,
        connection_tg,
        scheduler,
        chat_id,
        wb_db,
        tg_db,
    ):
        self.skidka_link = skidka_link
        self.connection_wb = connection_wb
        self.connection_tg = connection_tg
        self.scheduler = scheduler
        self.chat_id = chat_id
        self.wb_db = wb_db
        self.tg_db = tg_db
        self.time_h = int(datetime.now().strftime("%H"))
        self.bot = telebot.TeleBot(TOKEN)

    def get_short_link(self, link):
        result = requests.post(
            url="https://goo.su/api/links/create",
            headers={
                "content-type": "application/json",
                "x-goo-api-token": GOO_SO_TOKEN,
            },
            data=json.dumps({"url": link}),
        )
        if result.status_code == 200:
            return json.loads(result.text)["link"]["short"]

    def post_job(self, post):
        media = [
            types.InputMediaPhoto(url, parse_mode="HTML") for url in post["post_pic"]
        ]
        media[0].caption = post["post_text"]
        self.bot.send_media_group(chat_id=self.chat_id, media=media)

    def schedule_post(self, data, ad=False):
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

        global time_h
        self.time_h = (self.time_h + 1) % 24
        random_minute = randint(1, 15)

        self.scheduler.add_job(
            self.post_job,
            CronTrigger(hour=self.time_h, minute=random_minute),
            args=[data],
            name=task_name,
        )

    def get_delayed_posts(self):
        jobs = []
        jobs_list = self.scheduler.get_jobs()
        for job in jobs_list:
            run_time = job.next_run_time
            job_time = datetime.strptime(str(run_time), "%Y-%m-%d %H:%M:%S%z").strftime(
                "%d-%m %H:%M"
            )
            data = {"jobname": job.name, "jobtime": job_time, "job_id": job.id}
            jobs.append(data)
        return jobs

    def delete_job(self, job_id):
        self.scheduler.remove_job(job_id)

    def reschedule_post(self, data):
        jobs_list = self.scheduler.get_jobs()
        for job in jobs_list:
            print(job.id)

        user_job_id = data["job_id"]
        custom_hour = data["custom_hour"]
        custom_minute = data["custom_minute"]
        custom_day = data["custom_day"]
        custom_month = data["custom_month"]
        self.scheduler.reschedule_job(
            job_id=user_job_id,
            trigger=CronTrigger(
                day=custom_day,
                month=custom_month,
                hour=custom_hour,
                minute=custom_minute,
            ),
        )
        logging.debug(f"Rescheduled to time {custom_hour}:{custom_minute}")

    def append_data_to_db(self, wb_id, status):
        post_exist = tg_sql.is_post_in_db(wb_id, self.connection_tg)
        if post_exist:
            tg_sql.set_post_status(
                wb_id=wb_id, status=status, connection=self.connection_tg
            )
        elif post_exist == False:
            tg_sql.add_post(wb_id=wb_id, status=status, connection=self.connection_tg)

    def wbparse(self):
        all_products = sql.get_all_products(self.connection_wb)

        tg_posts: list = tg_sql.get_all_posts(self.connection_tg)
        filtered_products = [
            product for product in all_products if product["url"] not in tg_posts
        ]
        return filtered_products

    def format_post(self, item):
        name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        composition = item.get("composition")
        color = item.get("color")
        url = item.get("url")
        discount_percent = ((int(price) - int(discount_price)) / int(price)) * 100
        try:
            short_url = f"https://goo.su/{self.get_short_link(url)}"
        except:
            short_url = False
        title_emoji = choice(["♨️", "💯", "🔎", "📌", "🎈", "💥", "⚡️"])
        price_emoji = choice(["💸", "💰", "💵"])
        post = f"{title_emoji}{hbold(name)}" if name else ""
        post += (
            f"\n\n{price_emoji}Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽ (скидка {hbold(int(discount_percent))}%)"
            if price and discount_price
            else ""
        )
        if float(star_rating) >= 4.8:
            post += (
                f"\n\n⭐️{hbold('Хороший рейтинг')}: {hbold(star_rating)}"
                if star_rating
                else ""
            )
        else:
            post += f"\n\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""

        post += f"\n\n🔬Состав: {hbold(composition)}" if composition else ""
        post += f"\n\n🌈Цвет: {hbold(color)}" if color else ""
        post += (
            f"\n\n🔗{hbold('Купить здесь:')} {hlink(url=short_url, title='ссылка на товар')}"
            if short_url
            else url
        )

        return post

    def prepare_posts(self):
        try:
            posts_list: list = self.wbparse()
        except:
            return False
        for item in posts_list:
            posts_list.pop(0)
            url = item.get("url")
            wb_id = item.get("wb_id")
            is_in_db = tg_sql.is_post_in_db(url, self.connection_tg)
            post_status = tg_sql.get_post_status(url, self.connection_tg)
            if is_in_db and post_status in ["Liked", "Disliked"]:
                continue
            post, pic_url = self.format_post(item), item.get("pic_url")
            if len(pic_url) >= 80:
                pic_url = ast.literal_eval(pic_url)
            return post, pic_url, url

    def clear_tg(self):
        tg_sql.close_connection(self.connection_tg)
        tg_sql.clear_db(self.tg_db)

    def clear_wb(self):
        sql.close_connection(self.connection_wb)
        sql.clear_db(self.wb_db)

    def count_of_products_in_db(self):
        return len(sql.get_all_products(self.connection_wb))
