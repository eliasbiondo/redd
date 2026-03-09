"""Shared test configuration and fixtures."""

from __future__ import annotations

import pytest

from redd import AsyncRedd, Redd


@pytest.fixture
def client() -> Redd:
    """Sync REDD client with no throttle for faster test runs."""
    c = Redd(throttle=(0, 0), timeout=15.0)
    yield c
    c.close()


@pytest.fixture
async def async_client() -> AsyncRedd:
    """Async REDD client with no throttle for faster test runs."""
    c = AsyncRedd(throttle=(0, 0), timeout=15.0)
    yield c
    await c.close()
