"""REDD exceptions — structured error hierarchy."""

from __future__ import annotations


class ReddError(Exception):
    """Base exception for all REDD errors."""


class HttpError(ReddError):
    """Raised when an HTTP request fails after retries."""

    def __init__(self, status_code: int, url: str, detail: str = "") -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code} for {url}" + (f": {detail}" if detail else ""))


class ParseError(ReddError):
    """Raised when Reddit's JSON response cannot be parsed into domain models."""


class NotFoundError(ReddError):
    """Raised when a requested resource (user, post, subreddit) does not exist."""
