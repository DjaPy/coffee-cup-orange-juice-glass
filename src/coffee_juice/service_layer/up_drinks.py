from app.models import Drink
from app.schema.request import DrinkAddRequest, DrinkAddResponse


async def add_drink_data(drink_data: DrinkAddRequest) -> DrinkAddResponse:
    drink_result = await Drink.create(drink_type=drink_data.drink, volume=drink_data.volume)
    return DrinkAddResponse.from_orm(drink_result)
