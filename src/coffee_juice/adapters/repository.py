from typing import Any, List, Optional


from coffee_juice.adapters.orm import TestTable, TwoTestTable
from coffee_juice.entrypoints.api.schemas import ExampleCollection


async def update_bulk_data(data: List[ExampleCollection]) -> None:
    data_dicts = [example.dict() for example in data]
    await TestTable.insert().gino.all(data_dicts)


async def create_example(data: ExampleCollection):
    await TestTable.create(test_string=data.test_string)


async def update_example(data: ExampleCollection):
    await TestTable.update(test_string=data.test_string).apply()
