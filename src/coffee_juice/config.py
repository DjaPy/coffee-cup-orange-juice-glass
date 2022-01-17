from pathlib import Path
from typing import Any, Dict, List, Optional

from eo_kafka import KafkaClientsSettings
from pydantic import AnyHttpUrl, BaseSettings, Field, PostgresDsn, validator

from coffee_juice._base.aiohttp_client import ConfigClient
from coffee_juice.enums import AppEnvEnum


class KafkaConfig(KafkaClientsSettings):
    class Config:
        env_prefix = 'KAFKA_'
        env_file = '.env'


class ExampleHttpConfig(ConfigClient):

    class Config:
        env_prefix = 'EXAMPLE_'
        env_file = '.env'


class Config(BaseSettings):

    example_client: ExampleHttpConfig = ExampleHttpConfig()
    kafka: KafkaConfig = KafkaConfig()

    host: str = '127.0.0.1'
    port: int = 8000
    service_name: str = "coffee_cup_orange_juice_glass"
    app_env: AppEnvEnum = AppEnvEnum.test

    # CORS origins
    origins: List[Optional[AnyHttpUrl]] = []

    # База данных. DSN.
    db_server: str = 'db'
    db_port: str = '5432'
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_name: str = 'postgres'
    db_dsn: Optional[PostgresDsn] = None

    @validator('db_dsn', pre=True)
    def assemble_db_connection(cls, db_dsn: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(db_dsn, str):
            return db_dsn
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("db_user"),
            password=values.get("db_password"),
            host=values.get("db_server"),
            port=values.get("db_port"),
            path=f"/{values.get('postgres_db') or ''}",
        )

    # Настройки хранилища трейсов.
    jaeger_enable: bool = False
    jaeger_name: str = 'Core'
    jaeger_host: str = 'localhost'
    jaeger_port: int = 6831

    # Настройки логирования в sentry.
    sentry_enable: bool = False
    sentry_url: Optional[AnyHttpUrl]

    class Config:
        env_file = '.env'


config = Config()
