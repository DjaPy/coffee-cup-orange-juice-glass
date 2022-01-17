FROM python:3.9-slim

ENV FORWARDED_ALLOW_IPS=* \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/

COPY docker/entrypoint.sh docker/wait-for-it.sh prestart.sh pyproject.toml /

RUN apt update && apt install -y \
    libmagic1 \

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev && \
    rm -rf ~/.cache/pypoetry 

COPY alembic.ini /
COPY migrations /migrations
COPY src/coffee_juice /coffee_juice

CMD ["/entrypoint.sh"]
