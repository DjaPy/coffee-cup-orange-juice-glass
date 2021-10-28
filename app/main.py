from functools import partial

import uvicorn
from fastapi import FastAPI

from app.api import router
from app.config import config, Config
from app.infrastraction.connection import db


async def startup_db(app: FastAPI) -> None:
    conf = app.state.config
    await db.set_bind(conf.db_dsn)


async def shutdown_db() -> None:
    _bind = db.pop_bind()
    await _bind.close()


def get_application(app_config: Config) -> FastAPI:

    app = FastAPI(
        title='Educate Online API',
        description='Описание методов и моделей данных Educate Online API',
        docs_url='/doc',
    )
    app.state.config = app_config

    app.add_event_handler(event_type='startup', func=partial(startup_db, app=app))
    app.add_event_handler(event_type='shutdown', func=shutdown_db)

    app.include_router(router)

    return app


app_server = get_application(config)

if __name__ == "__main__":
    uvicorn.run(app_server, host=config.host, port=config.port)
