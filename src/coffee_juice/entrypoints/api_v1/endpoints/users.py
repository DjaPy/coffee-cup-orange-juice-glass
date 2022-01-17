
from fastapi import APIRouter, status

from coffee_juice.service_layer import up_drinks
from coffee_juice.entrypoints.api_v1.schema.request import DrinkAddRequest, DrinkAddResponse

router = APIRouter(prefix='/users')

bot = commands.Bot()


@router.post(
    '/drink',
    description='Добавление напитка',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {'model': DrinkAddRequest, 'description': 'Напиток добавлен'},
    },
)
async def add_drink(drink_data: DrinkAddRequest) -> DrinkAddResponse:
    return await up_drinks.add_drink_data(drink_data)
