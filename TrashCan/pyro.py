from pyrogram import Client, types, raw
from settings import *
from _datetime import datetime

app = Client(name=name_uset_admin, api_id=api_id, api_hash=api_hash)

async def main(image, date):
    async with app:
        await app.send_photo(channel, photo=image, caption="Set Total", schedule_date=date)

date = datetime(year=2022, month=6, day=17, hour=00, minute=9)
image = "url image"

app.run(main(image, date))