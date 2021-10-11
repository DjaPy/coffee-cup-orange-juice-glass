import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

from app.db import BaseDBModel
from app.enums import DrinkType


class User(BaseDBModel):
    __tablename__ = 'users'

    nickname = sa.Column(sa.String, nullable=False, comment='Имя пользователя')
    email = sa.Column(sa.String, nullable=False, comment='Почта пользователя')


class Drink(BaseDBModel):
    __tablename__ = 'Drinks'

    user_id = sa.Column(
        UUID,
        sa.ForeignKey('users.id', name='user_id_fkey'),
        nullable=False, comment='Идентификатор пользователя'
    )
    drink_type = sa.Column(
        ENUM(DrinkType),
        nullable=False,
        comment='Тип напитка',
    )
    volume = sa.Column(sa.DECIMAL)


