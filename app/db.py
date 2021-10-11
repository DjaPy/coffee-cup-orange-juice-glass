import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import sqlalchemy as sa
from gino import Gino
from sqlalchemy.dialects.postgresql import insert, UUID
from sqlalchemy.sql.elements import BinaryExpression

db = Gino()


class UUIDMixin:
    """
    Добавляет к модели поле id
    """
    __abstract__ = True
    id: uuid.UUID = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment='Идентификатор')

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self}>'

    def __str__(self) -> str:
        return f'{self.__class__.__name__} object ({self.id})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UUIDMixin):
            return False
        elif self.id is None:
            return self is other
        else:
            return self.__tablename__ == other.__tablename__ and self.id == other.id  # type: ignore

    def __hash__(self) -> Any:
        if self.id is None:
            raise TypeError('Model instances without primary key value are unhashable')
        return hash(self.id)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls.__abstract__ = False


class CreateUpdateMixin:
    """
    Добавляет к модели поля created_at и updated_at
    """
    __abstract__ = True
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=datetime.utcnow, server_default=sa.func.now())

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls.__abstract__ = False


class BaseDBModel(db.Model, UUIDMixin, CreateUpdateMixin):
    __abstract__ = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls.__abstract__ = False
        cls.__table_args__ = {'schema': 'main'}

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
        result = await cls.query.where(sa.and_(
            *[getattr(cls, key) == value for key, value in kwargs.items()]
        )).gino.first()
        if not result:
            result = await cls.create(**{**kwargs, **(defaults or {})})
            created = True
        return result, created
