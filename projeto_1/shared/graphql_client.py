from datetime import datetime
from http import HTTPStatus
import json
import aiohttp
from aiohttp import ClientResponse

from shared.exceptions.grapql_client_exceptions import Unauthorized, UnexpectedError
from core.constants import PERSIT_GRAPQHL_QUERIES

class GraphqlClient:
    async def execute_query(
        self,
        path: str, 
        query: str,
        auth_token: str
    ):
        if PERSIT_GRAPQHL_QUERIES:
            now = datetime.now().strftime('%d-%m-%Y_%H-%M-%S.%f')
            with open(f'resources/debug/{now}', 'w+') as f:
                f.write(query)
        authed_header = self.__get_auth_header(auth_token)
        data = json.dumps({'query': query})
        async with aiohttp.ClientSession(headers=authed_header) as session:
            async with session.post(path, data=data) as response:
                return await self.__handle_response(response)
    

    def __get_auth_header(self, token: str):
        return {
            'Authorization': f'Bearer {token}'
        }

    async def __handle_response(self, response: ClientResponse):
        payload = await response.json()
        status_code = response.status
        if status_code > HTTPStatus.OK:
            raw_error = str(await response.content.read())
            self.__handle_error(status_code, raw_error)
        return payload

    def __handle_error(self, status_code: int, error: str):
        if status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            raise UnexpectedError(error)
        if status_code == HTTPStatus.UNAUTHORIZED:
            raise Unauthorized(error)
