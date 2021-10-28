from discord.ext import commands
from fastapi import APIRouter, status

from app import services
from app.schema.request import DrinkAddResponse, DrinkAddRequest

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
    return await services.add_drink_data(drink_data)
