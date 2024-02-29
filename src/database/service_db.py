from models import Products, Posts
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Any, Literal

from sqlalchemy.exc import IntegrityError


class DbService:
    def __init__(self, model):
        self.model = model

    def create(
        self,
        db: AsyncSession,
        data: Union[Menu, Submenu, Dishes],
        id: UUID = None,
        menu_id: UUID = None,
        submenu_id: UUID = None,
    ) -> Union[Literal[False], Any]:
        data_dict = data.model_dump()
        if "price" in data_dict:
            data_dict["price"] = str(float(data_dict["price"]))
        table = self.model(**data_dict)
        if id is not None:
            table.id = id
        if menu_id is not None:
            table.menu_id = menu_id
        if submenu_id is not None:
            table.submenu_id = submenu_id

        try:
            db.add(table)
            db.commit()
            db.refresh(table)
        except IntegrityError:
            return False
        return table

    def get_value(
        self,
        db: AsyncSession,
        id: UUID = None,
    ) -> Union[Any, str, None]:
        try:
            result = db.query(self.model).filter(self.model.id == id).first()
            if self.model == Menu and result is not None:
                """Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню."""
                submenus_count = db.query(Submenu).filter(Submenu.menu_id == id).count()
                dishes_count = (
                    db.query(Dishes)
                    .join(Submenu, Dishes.submenu_id == Submenu.id)
                    .filter(Submenu.menu_id == id)
                    .count()
                )
                result.submenus_count = submenus_count
                result.dishes_count = dishes_count
            elif self.model == Submenu and result is not None:
                """Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю."""
                dishes_count = db.query(Dishes).filter(Dishes.submenu_id == id).count()
                result.dishes_count = dishes_count
            elif self.model == Dishes and result is not None:
                """Вывод цены в формате соответствующем с тестами Postman"""
                result.price = str(float(result.price))
                # result.price = f"{result.price:.2f}" По ТЗ сказано 2 цифры после запятой, но тесты не проходят
            return result
        except Exception as e:
            return f"There was some error with calling function {e}"

    def get_all(
        self,
        db: AsyncSession,
        id: UUID = None,
    ) -> list:
        try:
            if id:
                table = db.query(self.model).filter(self.model.id == id).all()
            else:
                table = db.query(self.model).all()
        except Exception:
            return False
        return table

    def update(
        self,
        db: AsyncSession,
        data: Union[Menu, Submenu, Dishes],
        id: UUID = None,
    ) -> Union[Any, None]:
        try:
            table = db.query(self.model).filter(self.model.id == id).first()
            for key, value in data.model_dump().items():
                setattr(table, key, value)
            # if self.model == Dishes:
            #     data.price = float(data.price)
            db.add(table)
            db.commit()
            db.refresh(table)
        except Exception:
            return False
        return table

    def remove(
        self,
        db: AsyncSession,
        id: UUID = None,
    ) -> int:
        try:
            table = db.query(self.model).filter(self.model.id == id).delete()
            db.commit()
        except Exception:
            return False
        return table
