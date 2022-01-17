from decimal import Decimal

from pydantic import BaseModel

from coffee_juice.enums import DrinkType


class DrinkAddRequest(BaseModel):
    drink: DrinkType
    volume: Decimal

    class Config:
        orm_mode = True
