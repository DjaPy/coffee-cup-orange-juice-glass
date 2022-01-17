import uuid
from typing import Any, Dict, List, Optional, Tuple

from gino import Gino
from gino.declarative import ModelType
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ENUM, UUID, insert
from sqlalchemy.sql.elements import BinaryExpression

from coffee_juice.enums import DrinkType
from coffee_juice._base.datetime_work import dt_now

convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


db = Gino(naming_convention=convention)

Model: ModelType = db.Model


class UUIDMixin:
    """
    Добавляет к модели поле id
    """
    __abstract__ = True
    id = db.Column(UUID, primary_key=True, default=uuid.uuid4, comment='Идентификатор')


class CreateUpdateMixin:
    """
    Добавляет к модели поля created и updated
    """
    __abstract__ = True
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated = db.Column(db.DateTime(timezone=True), onupdate=dt_now, server_default=func.now())


class DeleteMixin:
    """
    Добавляет к модели поле deleted
    """
    __abstract__ = True
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class BaseDBModel(Model, UUIDMixin, CreateUpdateMixin):
    __abstract__ = True

    @classmethod
    def bulk_upsert(
            cls,
            rows: List[Dict[str, Any]],
            unique_keys: Optional[List[str]] = None,
            index_where: Optional[BinaryExpression] = None,
            constraint: str = None,
            where: Optional[BinaryExpression] = None,
    ) -> 'BaseDBModel':
        if unique_keys or index_where or constraint:
            query = insert(cls.__table__).values(rows)
            set_ = dict(query.excluded)
            set_.pop('id', None)
            return query.on_conflict_do_update(
                index_elements=unique_keys,
                index_where=index_where,
                constraint=constraint,
                set_=set_,
                where=where
            ).returning(cls.__table__).gino.all()
        return db.insert(cls.__table__).values(rows).returning(cls.__table__).gino.all()

    @classmethod
    async def get_or_create(
        cls,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Tuple['BaseDBModel', bool]:
        created = False
        result = await cls.query.where(db.and_(
            *[getattr(cls, key) == value for key, value in kwargs.items()]
        )).gino.first()
        if not result:
            result = await cls.create(**{**kwargs, **(defaults or {})})
            created = True
        return result, created


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