import os, asyncio
from database.models import Products, Posts
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv("TOKEN")
GOO_SO_TOKEN = os.getenv("GOO_SO_TOKEN")

DB_TYPE = os.getenv("DB_TYPE")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

jobstores_database_url = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

jobstores = {"default": SQLAlchemyJobStore(url=jobstores_database_url)}
scheduler_tp = AsyncIOScheduler(jobstores=jobstores)
scheduler_bijou = AsyncIOScheduler(jobstores=jobstores)
scheduler_home = AsyncIOScheduler(jobstores=jobstores)
scheduler_tp.start()
scheduler_bijou.start()
scheduler_home.start()


categories = {
    "Бижутерия": {
        "skidka_category_link": "https://skidka7.com/discount/jew/all",
        "group_name": "Bijou",
        "tg_group_id": "2051501195",
        "scheduler": scheduler_bijou,
    },
    "Одежда тпшкам": {
        "skidka_category_link": "https://skidka7.com/discount/cwomen/all",
        "group_name": "Clothes",
        "tg_group_id": "2041578470",
        "scheduler": scheduler_tp,
    },
    "Для дома": {
        "skidka_category_link": "https://skidka7.com/discount/dom/all",
        "group_name": "Home",
        "tg_group_id": "1553355442",
        "scheduler": scheduler_home,
    },
}
