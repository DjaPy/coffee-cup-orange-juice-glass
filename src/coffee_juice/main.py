import uvicorn

from coffee_juice.config import config
from coffee_juice.entrypoints.fastapi_app import app_server

if __name__ == "__main__":
    uvicorn.run(app_server, host=config.host, port=config.port)
