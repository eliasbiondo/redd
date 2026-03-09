"""Asynchronous HTTP adapter using the ``httpx`` library.

``httpx`` is an **optional** dependency — it is only imported when the user
instantiates :class:`AsyncRedd` or this adapter directly.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from redd.adapters._user_agents import random_user_agent

logger = logging.getLogger("redd.http.async")


class HttpxAsyncAdapter:
    """``httpx``-based implementation of :class:`~redd.ports.http.AsyncHttpPort`.

    Parameters
    ----------
    proxy:
        Optional HTTP/HTTPS proxy URL.
    timeout:
        Default request timeout in seconds.
    rotate_user_agent:
        If *True*, send a random User-Agent header with every request.
    max_retries:
        Number of automatic retries on transient failures.
    """

    __slots__ = ("_client", "_rotate_ua", "_timeout")

    def __init__(
        self,
        *,
        proxy: str | None = None,
        timeout: float = 10.0,
        rotate_user_agent: bool = True,
        max_retries: int = 3,
    ) -> None:
        transport = httpx.AsyncHTTPTransport(retries=max_retries)
        self._client = httpx.AsyncClient(
            transport=transport,
            proxy=proxy,
            follow_redirects=True,
        )
        self._timeout = timeout
        self._rotate_ua = rotate_user_agent

    # ── AsyncHttpPort interface ───────────────────────────────────────────

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform an async GET request and return decoded JSON."""
        headers: dict[str, str] = {}
        if self._rotate_ua:
            headers["User-Agent"] = random_user_agent()

        effective_timeout = timeout if timeout is not None else self._timeout
        response = await self._client.get(url, params=params, headers=headers, timeout=effective_timeout)
        response.raise_for_status()
        logger.debug("GET %s → %s", url, response.status_code)
        result: dict[str, Any] = response.json()
        return result

    async def download(self, url: str, *, dest: str, timeout: float | None = None) -> str:
        """Stream-download a binary resource to *dest*."""
        headers: dict[str, str] = {}
        if self._rotate_ua:
            headers["User-Agent"] = random_user_agent()

        effective_timeout = timeout if timeout is not None else 30.0
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)

        async with self._client.stream("GET", url, headers=headers, timeout=effective_timeout) as response:
            response.raise_for_status()
            with open(dest, "wb") as fh:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    fh.write(chunk)

        logger.debug("Downloaded %s → %s", url, dest)
        return dest

    async def close(self) -> None:
        """Close the underlying ``httpx.AsyncClient``."""
        await self._client.aclose()

    # ── Async context manager support ─────────────────────────────────────

    async def __aenter__(self) -> HttpxAsyncAdapter:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
