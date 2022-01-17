from functools import partial
from typing import Any

import sentry_sdk
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.middleware.cors import CORSMiddleware

from coffee_juice.adapters.example_http.inner_http import example_http_client
from coffee_juice.adapters.orm import db
from coffee_juice._base.custom_serializers import json_serializer
from coffee_juice.config import Config, config
from coffee_juice.entrypoints.api_v1.api import api_router
from coffee_juice.service_layer.consumers import EVENTS_TO_CONSUME

resource = Resource(attributes={
    "service.name": config.jaeger_name
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name=config.jaeger_host,
    agent_port=config.jaeger_port,
)
trace.get_tracer_provider().add_span_processor(  # type: ignore
    BatchSpanProcessor(jaeger_exporter, max_export_batch_size=10)
)


if config.sentry_enable and config.sentry_url:
    sentry_sdk.init(dsn=config.sentry_url)


async def startup_db(app: FastAPI) -> None:
    conf = app.state.config
    await db.set_bind(conf.db_dsn, json_serializer=json_serializer)


async def start_kafka_clients() -> None:
    await KAFKA_CLIENTS.start_producer()
    await KAFKA_CLIENTS.start_consumers(EVENTS_TO_CONSUME)


async def shutdown_db() -> None:
    _bind = db.pop_bind()
    await _bind.close()


def get_application(app_config: Config) -> FastAPI:

    app = FastAPI(
        title='coffee cup',
        description='Base description',
        docs_url='/doc',
        on_startup=[
            example_http_client.start,
        ],
        on_shutdown=[
            shutdown_db,
            example_http_client.stop,
        ],
    )

    app.state.config = app_config

    allow_origins = [str(origin) for origin in app_config.origins]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ['*'],  # todo: Поменять когда релизнимся
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_event_handler(event_type='startup', func=partial(startup_db, app=app))

    app.include_router(api_router)

    if app_config.jaeger_enable:
        FastAPIInstrumentor.instrument_app(app, excluded_urls='/openapi.json|/doc')
        AioHttpClientInstrumentor().instrument()

    return app


app_server = get_application(config)


@app_server.middleware("http")
async def sentry_exception(request: Request, call_next: Any) -> Any:
    if config.sentry_enable is False:
        return await call_next(request)
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_context('request', request)   # type: ignore
            user_id = 'user_id'  # when available
            scope.user = {'ip_address': request.client.host, 'id': user_id}
            sentry_sdk.capture_exception(e)
        raise e
