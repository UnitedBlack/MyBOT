from models import Products, Posts
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Union, Any, Literal

from sqlalchemy.exc import IntegrityError


# class DbService:
#     def __init__(
#         self,
#         db_session: AsyncSession,
#         table: Union[Posts, Products],
#     ) -> Any:
#         db_session = db_session
#         table = table


async def add_post(
    db_session: AsyncSession,
    table: Union[Posts, Products],
    data: dict[Any],
) -> Any:
    try:
        obj = table(**data)
        db_session.add(obj)
        await db_session.commit()
    except IntegrityError as e:
        db_session.rollback()
        raise ValueError("Data Integrity Error Occured") from e
    except Exception as e:
        db_session.rollback()
        raise e


async def get_all_posts(
    db_session: AsyncSession,
    table: Union[Posts, Products],
) -> list:
    query = db_session.select(table.wb_id)
    result = await db_session.execute(query)
    wb_ids = [row[0] for row in result.scalars.all()]
    return wb_ids


async def update_post_status(
    db_session: AsyncSession,
    table: Union[Posts, Products],
    status,
    id,
) -> None:
    query = update(table).filter(table.wb_id == id).values(status=status)
    await db_session.execute(query)
    await db_session.commit()


async def get_post_status(
    db_session: AsyncSession,
    table: Union[Posts, Products],
    id_to_check,
) -> Any | Literal[False]:
    query = select(table).filter(table.wb_id == id_to_check)
    result = await db_session.execute(query)
    row = result.first()
    return row[0] if row else False


async def is_post_in_db(
    db_session: AsyncSession,
    table: Union[Posts, Products],
    id_to_check,
) -> bool:
    query = select(table).where(table.wb_id == id_to_check)
    result = await db_session.execute(query)
    row = result.fetchone()
    return row if row else False


################################################
# PRODUCTS
async def get_all_products(
    db_session: AsyncSession,
    table: Union[Posts, Products],
) -> list:
    query = select(table)
    result = await db_session.execute(query)
    rows = result.fetchall()
    column_names = result.keys()
    result_dicts = [dict(zip(column_names, row)) for row in rows]
    return result_dicts


async def is_product_in_database(
    db_session: AsyncSession,
    table: Union[Posts, Products],
    url_to_check,
) -> bool:
    query = select(table.url).where(table.url == url_to_check)
    result = await db_session.execute(query)
    row = result.fetchone()
    return row is not None


async def delete_all_records(
    db_session: AsyncSession,
    table: Union[Posts, Products],
) -> None:
    query = delete(table)
    await db_session.execute(query)
    await db_session.commit()

    # def create(
    #     self,
    #     db: AsyncSession,
    #     data: Union[Menu, Submenu, Dishes],
    #     id: UUID = None,
    #     menu_id: UUID = None,
    #     submenu_id: UUID = None,
    # ) -> Union[Literal[False], Any]:
    #     data_dict = data.table_dump()
    #     if "price" in data_dict:
    #         data_dict["price"] = str(float(data_dict["price"]))
    #     table = table(**data_dict)
    #     if id is not None:
    #         table.id = id
    #     if menu_id is not None:
    #         table.menu_id = menu_id
    #     if submenu_id is not None:
    #         table.submenu_id = submenu_id

    #     try:
    #         db.add(table)
    #         db.commit()
    #         db.refresh(table)
    #     except IntegrityError:
    #         return False
    #     return table

    # def get_value(
    #     self,
    #     db: AsyncSession,
    #     id: UUID = None,
    # ) -> Union[Any, str, None]:
    #     try:
    #         result = db.query(table).filter(table.id == id).first()
    #         if table == Menu and result is not None:
    #             """Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню."""
    #             submenus_count = db.query(Submenu).filter(Submenu.menu_id == id).count()
    #             dishes_count = (
    #                 db.query(Dishes)
    #                 .join(Submenu, Dishes.submenu_id == Submenu.id)
    #                 .filter(Submenu.menu_id == id)
    #                 .count()
    #             )
    #             result.submenus_count = submenus_count
    #             result.dishes_count = dishes_count
    #         elif table == Submenu and result is not None:
    #             """Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю."""
    #             dishes_count = db.query(Dishes).filter(Dishes.submenu_id == id).count()
    #             result.dishes_count = dishes_count
    #         elif table == Dishes and result is not None:
    #             """Вывод цены в формате соответствующем с тестами Postman"""
    #             result.price = str(float(result.price))
    #             # result.price = f"{result.price:.2f}" По ТЗ сказано 2 цифры после запятой, но тесты не проходят
    #         return result
    #     except Exception as e:
    #         return f"There was some error with calling function {e}"

    # def get_all(
    #     self,
    #     db: AsyncSession,
    #     id: UUID = None,
    # ) -> list:
    #     try:
    #         if id:
    #             table = db.query(table).filter(table.id == id).all()
    #         else:
    #             table = db.query(table).all()
    #     except Exception:
    #         return False
    #     return table

    # def update(
    #     self,
    #     db: AsyncSession,
    #     data: Union[Menu, Submenu, Dishes],
    #     id: UUID = None,
    # ) -> Union[Any, None]:
    #     try:
    #         table = db.query(table).filter(table.id == id).first()
    #         for key, value in data.table_dump().items():
    #             setattr(table, key, value)
    #         # if table == Dishes:
    #         #     data.price = float(data.price)
    #         db.add(table)
    #         db.commit()
    #         db.refresh(table)
    #     except Exception:
    #         return False
    #     return table

    # def remove(
    #     self,
    #     db: AsyncSession,
    #     id: UUID = None,
    # ) -> int:
    #     try:
    #         table = db.query(table).filter(table.id == id).delete()
    #         db.commit()
    #     except Exception:
    #         return False
    #     return table
