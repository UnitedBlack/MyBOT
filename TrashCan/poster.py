# from aiogram import Bot, Dispatcher, types
# from aiogram.utils import executor
# from aiogram.utils.markdown import hbold, hstrikethrough
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram import types
# from aiogram.types import InputMediaPhoto
# from configure_bot import TOKEN
# import sql, tg_sql, ast, logging, json, os, asyncio
# from pprint import pprint
# from main import initialize
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from datetime import datetime
# from apscheduler.triggers.cron import CronTrigger

# post_hour = 0
# scheduler = AsyncIOScheduler()


# async def post_job(data):
#     post_text = data['post_text']
#     pics = data['pic_url']
#     await bot.send_message(chat_id="333253716", text=data)


# async def schedule_post(text_data):
#     global post_hour
#     if post_hour >= 24:
#         post_hour = 0
#     else:
#         post_hour += 1
#     print(post_hour)
#     scheduler.add_job(post_job, CronTrigger(se=post_hour), args=[text_data])


# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot, storage=MemoryStorage())


# # async def to_post():
# #     bot.


# async def get_group_id():
#     chat = await bot.get_chat(chat_id="@ozonwbdiscount")
#     print(chat.id)


# @dp.message_handler(commands=["start"], state="*")
# async def start_point(message: types.Message):
#     # await get_group_id()
#     await schedule_post("ААААА")


# if __name__ == "__main__":
#     #     # asyncio.run(get_group_id())
#     scheduler.start()
#     executor.start_polling(dp, skip_updates=True)


import requests, json
from pprint import pprint
from datetime import datetime

# data = {"message": "Hello, Flask!"}
headers = {"Content-Type": "application/json"}

# uebanstvo = {
#     "pics": [
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/1.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/2.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/3.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/4.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/5.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/6.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/7.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/8.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/9.webp",
#         "https://basket-10.wb.ru/vol1548/part154855/154855340/images/big/10.webp",
#     ],
#     "post": "asdsadsda",
# }

# text = {"text": "Привет, я APScheduler"}

# data = {"get_delayed_posts": "get_delayed_posts"}

# # data = {"job_id": "6438e02128ea468888e2e034c2b7cec1"}
# # data = {"post_text": "Fadfasdfa", "post_pic": "asdsdaads", "custom_time": "05"}
# pprint(
#     requests.post(
#         # url="https://inlinegptbot.unitedblack.repl.co",
#         url = "http://127.0.0.1:80",
#         data=json.dumps(data),
#         headers=headers,
#     ).text
# )
# %d-%m %H:%M
# date = "31-10 23:00"
# strp_date = datetime.strptime(str(date), "%d-%m %H:%M")
# day = strp_date.day
# month = strp_date.month
# hour = strp_date.hour

# print(day, month, hour)
from configure_bot import GOO_SO_TOKEN


def get_short_link(
    link="https://www.wildberries.ru/catalog/184649387/detail.aspx",
) -> str:
    result = requests.post(
        url="https://goo.su/api/links/create",
        headers={"content-type": "application/json", "x-goo-api-token": GOO_SO_TOKEN},
        data=json.dumps(
            {"url": "https://www.wildberries.ru/catalog/184649387/detail.aspx"}
        ),
    )
    if result.status_code == 200:
        print(json.loads(result.text)["link"]["short"])


# {
#     "successful": true,
#     "succes": true,
#     "message": "Link successfully created",
#     "link": {
#         "long_url": "https:\/\/www.wildberries.ru\/catalog\/184649387\/detail.aspx",
#         "short": "QetvgRB",
#         "hits": 0,
#         "group": null,
#     },
#     "short_url": "https:\/\/goo.su\/QetvgRB",
#     "qr": {
#         "base64": "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsAQAAAABRBrPYAAAABGdBTUEAALGPC\/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAd2KE6QAAAGbSURBVGje7ZpdjsMgDIR549j0yL6Bt9kQPLbZvMYbDUJtGr4gVcR\/A62t1vX8HtKGHq1tG7F\/iB3kl+kaRs82LwSwNUSsDDY\/+8EMmat\/3nGAx2ZXYtWxac73a\/r7MthUxMpjaM53WJ9OgFhpTCC2Jsw8uZgtm29XYmWwXY5kC7pNpUInVhnzZouDCm06Z3htZhNiJbCQ5Q4fUtGcF6aQaBErjXmvO1IZOy43bjEaqqQ5D7E6WI6qmDKt\/Aq0i\/UyqNgdYlUw8cYIazogE0bVAl06sXJYc9e2xF1xSCWac\/Dn5+TEKmDb7NcibFricdVH4aeKPUXsYSykSQuTmCbhPCsuE6uJhdQIlzVXrypOY0Q1g1g1bFPXZJ8M9h61RHiWWCksZsIX5hSMbrmWacjEymAbjRflwb7x0jYn9KweEyuB+VIo7+nEHYHWopRBrAYWRPubcjVguRYmVhPLxpsdsmap\/y3Y52X\/tO0q1tbuTsLITi4mVgZDtTDXpy4o40FEv61D7Hlsd7bBTg\/+scOusKEzBeR8aoLYM9gP5Vxk70TFt9cAAAAASUVORK5CYII="
#     },
# }
get_short_link()
