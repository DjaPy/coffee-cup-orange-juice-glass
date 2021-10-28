from sqlalchemy.dialects.postgresql import UUID, ENUM

from app.infrastraction.base import BaseDBModel
from app.infrastraction.connection import db
from app.enums import DrinkType


class User(BaseDBModel):
    __tablename__ = 'users'

    nickname = db.Column(db.String, nullable=False, comment='Имя пользователя')
    telegram_number = db.Column(db.String, nullable=False, comment='Почта пользователя')


class Drink(BaseDBModel):
    __tablename__ = 'drinks'

    user_id = db.Column(
        UUID,
        db.ForeignKey('users.id', name='user_id_fkey'),
        nullable=False, comment='Идентификатор пользователя'
    )
    drink_type = db.Column(
        ENUM(DrinkType),
        nullable=False,
        comment='Тип напитка',
    )
    volume = db.Column(db.DECIMAL, nullable=True, comment='Объём напитка')


