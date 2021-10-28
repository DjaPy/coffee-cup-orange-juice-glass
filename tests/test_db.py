import pytest

from app.enums import DrinkType
from app.models import Drink, User


@pytest.mark.asyncio
async def test_start(server, fake):
    user = await User.create(nickname='Totty', email=fake.email())
    drink = await Drink.create(user_id=user.id, drink_type=DrinkType.juice, volume=200)
    assert drink
