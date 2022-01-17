from fastapi import APIRouter

from coffee_juice.entrypoints.api_v1.endpoints import health_check

api_router = APIRouter()
api_router.include_router(health_check.router, prefix='/health-check', tags=['Health check'])
