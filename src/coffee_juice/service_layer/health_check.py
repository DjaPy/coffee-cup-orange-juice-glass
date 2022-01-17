from coffee_juice.enums import HealthStatus


async def check_s3_connect() -> HealthStatus:
    health_status = HealthStatus.ok
    return health_status
