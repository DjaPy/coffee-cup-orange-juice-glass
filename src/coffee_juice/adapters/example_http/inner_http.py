from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import UUID4, BaseModel

from coffee_juice._base.aiohttp_client import Client, repeat_call_on_exception
from coffee_juice.config import ExampleHttpConfig, config
from coffee_juice.adapters.example_http.schemas import TestResponseSchema


class ExampleClientException(Exception):
    """Исключение для example HTTP клиента."""


ResponseModel = TypeVar('ResponseModel', bound=BaseModel)


class ExampleHttpClient(Client[ExampleHttpConfig, Exception]):
    _exception = ExampleClientException

    async def _call(
        self,
        method: str,
        path: str,
        response_schema: Type[ResponseModel],
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Optional[Any],
    ) -> ResponseModel:
        try:
            response = await self._send_request(
                method=method,
                response_schema=response_schema,
                path=path,
                headers=headers,
                **kwargs,
            )
        except Exception as exc:
            pass
        return response

    async def test_request_service(self, token: str) -> Optional[TestResponseSchema]:
        headers = {'Authorization': f'Bearer {token}'}
        test_data = await self._call(
            method='GET',
            response_schema=TestResponseSchema,
            path='/test/test_response',
            headers=headers,
        )
        return test_data


example_http_client = ExampleHttpClient(config.example_client)
