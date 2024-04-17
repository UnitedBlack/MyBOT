import ast
from typing import Union
from database import service_db
from database.models import Posts, Products
from . import format


class ScrapyCore:
    def __init__(
        self,
        skidka_link: str,
        group_name: str,
        scheduler,
        tg_group_id: str,
    ) -> None:
        self.skidka_link = skidka_link
        self.group_name = group_name
        self.scheduler = scheduler
        self.tg_group_id = tg_group_id

    def wbparse(self):
        all_products = service_db.get_all_products(group_name=self.group_name)
        tg_posts = service_db.get_all_posts(group_name=self.group_name)
        filtered_products = [
            product for product in all_products if product["url"] not in tg_posts
        ]
        return filtered_products

    def prepare_posts(self):
        try:
            posts_list: list = self.wbparse()
        except:
            return False

        for item in posts_list:
            posts_list.pop(0)
            url = item.get("url")
            wb_id = item.get("wb_id")
            service_db.is_post_in_db(self.db_session, id)
            is_in_db = service_db.is_post_in_db(
                db_session=...,
                id_to_check=url,
                group_name=self.group_name,
            )  # url = id_to_check
            post_status = service_db.get_post_status(
                db_session=...,
                id_to_check=url,
                group_name=self.group_name,
            )
            if is_in_db and post_status in ["Liked", "Disliked"]:
                continue
            post = format.format_post(item)
            pic_url = item.get("pic_url")
            if len(pic_url) >= 80:
                pic_url = ast.literal_eval(pic_url)
            return post, pic_url, url

def append_data_to_db(wb_id, status, group_name):
    post_exist = service_db.is_post_in_db(wb_id, group_name=group_name)
    if post_exist:
        service_db.update_post_status(
            id=wb_id, status=status, group_name=group_name
        )
    elif post_exist == False:
        data = Posts(wb_id=wb_id, status=status, group_name=group_name)
        service_db.add_post(
            data=data,
            table_name=Posts,
        )

async def get_data_from_db(model: Union[Posts | Products], session, group_name):
    if model == Posts:
        data = await service_db.get_all_posts(
            db_session=session,
            group_name=group_name,
        )

    elif model == Products:
        data = await service_db.get_all_products(
            db_session=session,
            group_name=group_name,
        )
    return data
