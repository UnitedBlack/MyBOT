from sqlalchemy import Column, String, DECIMAL, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class Products(Base):
    __tablename__ = "product"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    wb_id = Column(
        Integer,
        unique=True,
        nullable=False,
    )
    group = Column(String(150))
    name = Column(String(150))
    discount_price = Column(Integer)
    price = Column(Integer)
    star_rating = Column(DECIMAL)
    url = Column(String(150))
    pic_url = Column(String(150))
    composition = Column(String(150))
    size = Column(String(150))
    color = Column(String(150))


class Posts(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    wb_id = Column(
        Integer,
        unique=True,
        nullable=False,
    )
    group = Column(String(150))
    status = Column(String(150))
