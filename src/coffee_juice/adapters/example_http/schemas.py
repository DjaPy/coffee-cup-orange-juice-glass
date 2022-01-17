from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ExampleCollection(BaseModel):
    test_string: str
    test_integer: int
    test_float: float


class TestResponseSchema(BaseModel):

    list_collections: List[ExampleCollection]
    test_datetime: Optional[datetime] = Field(title='Дата и время',  description='Дата и время')
