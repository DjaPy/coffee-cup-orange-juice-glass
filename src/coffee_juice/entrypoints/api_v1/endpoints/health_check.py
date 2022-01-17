from fastapi import APIRouter
from starlette import status

from coffee_juice import __version__
from coffee_juice.entrypoints.custom_route import OpenTelemetryRoute
from coffee_juice.entrypoints.api_v1.schema.response import HealthResponseSchema
from coffee_juice.service_layer import health_check

router = APIRouter(route_class=OpenTelemetryRoute)


@router.get(
    '/',
    summary='Проверка работы сервиса',
    responses={
        status.HTTP_200_OK: {'model': HealthResponseSchema, 'description': 'Сервис работает'},
    },
)
async def health_check() -> HealthResponseSchema:
    check_s3 = await health_check.check_s3_connect()
    return HealthResponseSchema(version=__version__, s3=check_s3)
