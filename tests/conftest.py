import asyncio
import uuid
from functools import partial
from typing import List, Optional

import pytest
import sqlalchemy as sa
import uvicorn
from aiohttp import request
from faker import Faker
from fastapi import FastAPI
from sqlalchemy.engine.url import URL
from sqlalchemy_utils import create_database, drop_database

from app.config import Config
from app.infrastraction.connection import db
from app.main import get_application

pytest_plugins = ['fixtures_generate_data']


class UvicornTestServer(uvicorn.Server):
    """Uvicorn тестовый сервер.

    Подсмотренно тут
    https://github.com/miguelgrinberg/python-socketio/issues/332#issuecomment-712928157
    """

    def __init__(self, app: FastAPI, host: str, port: int):
        """Create a Uvicorn test server

        Args:
            app (FastAPI, optional): the FastAPI app. Defaults to main.app.
            host (str, optional): the host ip. Defaults to '127.0.0.1'.
            port (int, optional): the port. Defaults to PORT.
        """
        self._startup_done = asyncio.Event()
        super().__init__(config=uvicorn.Config(app, host=host, port=port))

    async def startup(self, sockets: Optional[List] = None) -> None:
        """Override uvicorn startup"""
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def up(self) -> None:
        """Start up server asynchronously"""
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def down(self) -> None:
        """Shut down server asynchronously"""
        self.should_exit = True
        await self._serve_task


@pytest.fixture
def fake():
    return Faker('ru-RU')


@pytest.fixture(scope='session')
def config():
    config = Config()
    return config


@pytest.fixture(scope='session')
def get_db_url(config):
    def _inner(driver, db_name):
        return URL(
            driver,
            username=config.db_user,
            password=config.db_password,
            host=config.db_server,
            port=int(config.db_port),
            database=db_name,
        )
    return _inner


@pytest.fixture(scope='session')
def test_db_name():
    test_db_name = f'{uuid.uuid4().hex}_pytest'
    return test_db_name


@pytest.fixture
async def engine_fixture(config, get_db_url, test_db_name):
    """
    На основе опыта Yandex
    http://www.moscowpython.ru/meetup/69/talk-from-yandex/
    """
    db_url = get_db_url('postgresql', test_db_name)

    create_database(db_url)

    engine = sa.create_engine(db_url)

    db.create_all(bind=engine, tables=db.sorted_tables)

    config.db_dsn = db_url

    yield

    for table in reversed(db.sorted_tables):
        ...
    drop_database(db_url)


@pytest.fixture
def app(config, engine_fixture):
    app = get_application(config)
    return app


@pytest.fixture
async def server(monkeypatch, config, aiohttp_unused_port, app):
    """Start server as test fixture and tear down after test"""
    config.port = aiohttp_unused_port()
    server_uvicorn = UvicornTestServer(app, config.host, config.port)
    await server_uvicorn.up()
    yield server
    await server_uvicorn.down()


@pytest.fixture
async def client(config):
    class _Client:
        def __getattribute__(self, item):
            return partial(request, method=item)

    return _Client()
