from pydantic import BaseModel, Field

from coffee_juice.enums import HealthStatus


class HealthResponseSchema(BaseModel):
    status: HealthStatus = HealthStatus.ok
    s3: HealthStatus = HealthStatus.ok
    version: str = Field(description='Версия билда')
