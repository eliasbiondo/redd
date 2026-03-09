"""Synchronous HTTP adapter using the ``requests`` library."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from redd.adapters._user_agents import random_user_agent

logger = logging.getLogger("redd.http.sync")

# ──────────────────────────────────────────────────────────────────────────────
# Default retry policy
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_RETRY = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)


class RequestsHttpAdapter:
    """``requests``-based implementation of :class:`~redd.ports.http.HttpPort`.

    Parameters
    ----------
    proxy:
        Optional HTTP/HTTPS proxy URL (e.g. ``"http://user:pass@host:port"``).
    timeout:
        Default request timeout in seconds.
    rotate_user_agent:
        If *True*, send a random User-Agent header with every request.
    retry:
        Custom :class:`urllib3.util.retry.Retry` policy.  Falls back to
        ``_DEFAULT_RETRY`` when *None*.
    """

    __slots__ = ("_rotate_ua", "_session", "_timeout")

    def __init__(
        self,
        *,
        proxy: str | None = None,
        timeout: float = 10.0,
        rotate_user_agent: bool = True,
        retry: Retry | None = None,
    ) -> None:
        self._session = requests.Session()
        self._timeout = timeout
        self._rotate_ua = rotate_user_agent

        adapter = HTTPAdapter(max_retries=retry or _DEFAULT_RETRY)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        if proxy:
            self._session.proxies.update({"http": proxy, "https": proxy})

    # ── HttpPort interface ────────────────────────────────────────────────

    def get(self, url: str, *, params: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
        """Perform a GET request and return decoded JSON."""
        if self._rotate_ua:
            self._session.headers["User-Agent"] = random_user_agent()

        effective_timeout = timeout if timeout is not None else self._timeout
        response = self._session.get(url, params=params, timeout=effective_timeout)
        response.raise_for_status()
        logger.debug("GET %s → %s", url, response.status_code)
        result: dict[str, Any] = response.json()
        return result

    def download(self, url: str, *, dest: str, timeout: float | None = None) -> str:
        """Stream-download a binary resource to *dest*."""
        if self._rotate_ua:
            self._session.headers["User-Agent"] = random_user_agent()

        effective_timeout = timeout if timeout is not None else 30.0
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)

        response = self._session.get(url, stream=True, timeout=effective_timeout)
        response.raise_for_status()

        with open(dest, "wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                fh.write(chunk)

        logger.debug("Downloaded %s → %s", url, dest)
        return dest

    def close(self) -> None:
        """Close the underlying ``requests.Session``."""
        self._session.close()

    # ── Context manager support ───────────────────────────────────────────

    def __enter__(self) -> RequestsHttpAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
