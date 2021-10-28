from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, validator, BaseSettings


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {'postgresql+asyncpg'}


class AppEnvEnum(str, Enum):
    prod = 'prod'
    dev = 'dev'
    test = 'test'


class Config(BaseSettings):

    host: str = Field('127.0.0.1', description='Хост сервера')
    port: int = Field(8000, description='Порт сервера')
    app_env: AppEnvEnum = Field(AppEnvEnum.prod, description='Среда выполнения. Возможные значения: prod, dev, test')
    site_name: str = Field('Coffe cup ', description='Название сайта')

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
        env_file = ".env"


config = Config()
