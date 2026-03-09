"""HTTP port — the interface that adapters must implement."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HttpPort(Protocol):
    """Contract for HTTP transports used by REDD clients."""

    def get(self, url: str, *, params: dict[str, Any] | None = None, timeout: float = 10.0) -> dict[str, Any]:
        """Perform a synchronous GET request and return decoded JSON."""
        ...

    def download(self, url: str, *, dest: str, timeout: float = 30.0) -> str:
        """Download a binary resource to *dest* and return the file path."""
        ...

    def close(self) -> None:
        """Release underlying resources."""
        ...


@runtime_checkable
class AsyncHttpPort(Protocol):
    """Contract for async HTTP transports used by AsyncRedd."""

    async def get(self, url: str, *, params: dict[str, Any] | None = None, timeout: float = 10.0) -> dict[str, Any]:
        """Perform an async GET request and return decoded JSON."""
        ...

    async def download(self, url: str, *, dest: str, timeout: float = 30.0) -> str:
        """Download a binary resource to *dest* and return the file path."""
        ...

    async def close(self) -> None:
        """Release underlying resources."""
        ...
