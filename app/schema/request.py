from decimal import Decimal

from pydantic import BaseModel

from app.enums import DrinkType


class DrinkAddRequest(BaseModel):
    drink: DrinkType
    volume: Decimal

    class Config:
        orm_mode = True


class DrinkAddResponse(BaseModel):
    drink_type: DrinkType
    volume: Decimal

    class Config:
        orm_mode = True