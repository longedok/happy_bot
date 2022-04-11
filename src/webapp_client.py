from __future__ import annotations

import os
from logging import getLogger
from typing import Any

import httpx
from httpx import Response

logger = getLogger(__name__)


class WebappClient:
    BASE_URL = os.environ.get("WEBAPP_URL")

    async def _post(self, url: str, data: dict, **request_params: Any) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, **request_params)

        logger.debug("POST response: %s", response)
        return response

    async def _get(
        self,
        url: str,
        params: dict[str, Any],
        **request_params: Any,
    ) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, **request_params)

        return response

    async def make_bot_token(self, token: str) -> dict:
        response = await self._post(
            f"{self.BASE_URL}/_int/users/bot_token/",
            {
                "token": token,
            },
        )
        return response.json()
