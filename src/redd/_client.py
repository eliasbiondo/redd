"""Synchronous Reddit client."""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Any
from urllib.parse import urlparse

from redd._exceptions import HttpError
from redd._parsing import (
    parse_post_detail,
    parse_search_results,
    parse_subreddit_posts,
    parse_user_items,
)
from redd.adapters.http_sync import RequestsHttpAdapter
from redd.domain.enums import Category, SortOrder, TimeFilter, UserCategory
from redd.domain.models import PostDetail, SearchResult, SubredditPost, UserItem

logger = logging.getLogger("redd")

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

_BASE = "https://www.reddit.com"
_BATCH_LIMIT = 100  # Reddit's max per-page


class Redd:
    """Synchronous Reddit scraper.

    Parameters
    ----------
    proxy:
        Optional HTTP/HTTPS proxy URL.
    timeout:
        Default request timeout in seconds.
    rotate_user_agent:
        Rotate User-Agent headers per-request to reduce ban risk.
    throttle:
        Tuple ``(min_seconds, max_seconds)`` for random sleep between
        paginated requests.  Set to ``(0, 0)`` to disable.

    Example
    -------
    >>> from redd import Redd
    >>> with Redd() as r:
    ...     results = r.search("Python", limit=5)
    ...     for item in results:
    ...         print(item.title)
    """

    __slots__ = ("_http", "_throttle")

    def __init__(
        self,
        *,
        proxy: str | None = None,
        timeout: float = 10.0,
        rotate_user_agent: bool = True,
        throttle: tuple[float, float] = (1.0, 2.0),
    ) -> None:
        self._http = RequestsHttpAdapter(
            proxy=proxy,
            timeout=timeout,
            rotate_user_agent=rotate_user_agent,
        )
        self._throttle = throttle

    # ── Context manager ───────────────────────────────────────────────────

    def __enter__(self) -> Redd:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        """Release underlying HTTP resources."""
        self._http.close()

    # ── Helpers ───────────────────────────────────────────────────────────

    def _sleep(self) -> None:
        lo, hi = self._throttle
        if hi > 0:
            time.sleep(random.uniform(lo, hi))

    def _get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        try:
            return self._http.get(url, params=params)
        except Exception as exc:
            logger.error("Request failed: %s", exc)
            raise HttpError(0, url, str(exc)) from exc

    # ── Public API ────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        *,
        limit: int = 25,
        sort: SortOrder = SortOrder.RELEVANCE,
        after: str | None = None,
        before: str | None = None,
    ) -> list[SearchResult]:
        """Search all of Reddit for posts matching *query*.

        Parameters
        ----------
        query:
            Search keywords.
        limit:
            Maximum number of results to return.
        sort:
            Sort order for the results.
        after / before:
            Pagination cursors.

        Returns
        -------
        list[SearchResult]
        """
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, _BATCH_LIMIT),
            "sort": sort.value,
            "type": "link",
        }
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        data = self._get(f"{_BASE}/search.json", params)
        return parse_search_results(data)[:limit]

    def search_subreddit(
        self,
        subreddit: str,
        query: str,
        *,
        limit: int = 25,
        sort: SortOrder = SortOrder.RELEVANCE,
        after: str | None = None,
        before: str | None = None,
    ) -> list[SearchResult]:
        """Search within a specific subreddit.

        Parameters
        ----------
        subreddit:
            Subreddit name (without ``r/`` prefix).
        query:
            Search keywords.
        limit:
            Maximum number of results.
        sort:
            Sort order.
        after / before:
            Pagination cursors.

        Returns
        -------
        list[SearchResult]
        """
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, _BATCH_LIMIT),
            "sort": sort.value,
            "type": "link",
            "restrict_sr": "on",
        }
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        data = self._get(f"{_BASE}/r/{subreddit}/search.json", params)
        return parse_search_results(data)[:limit]

    def get_post(self, permalink: str) -> PostDetail:
        """Scrape full post details including comment tree.

        Parameters
        ----------
        permalink:
            Reddit permalink path, e.g.
            ``"/r/Python/comments/abc123/my_post/"``.

        Returns
        -------
        PostDetail
        """
        permalink = permalink.rstrip("/")
        url = f"{_BASE}{permalink}.json"
        data = self._get(url, {"raw_json": 1})
        return parse_post_detail(data)

    def get_user(self, username: str, *, limit: int = 25) -> list[UserItem]:
        """Scrape a user's recent public activity.

        Parameters
        ----------
        username:
            Reddit username (without ``u/`` prefix).
        limit:
            Maximum number of items to fetch (paginated automatically).

        Returns
        -------
        list[UserItem]
        """
        url = f"{_BASE}/user/{username}/.json"
        items: list[UserItem] = []
        after: str | None = None

        while len(items) < limit:
            params: dict[str, Any] = {
                "limit": min(_BATCH_LIMIT, limit - len(items)),
                "raw_json": 1,
            }
            if after:
                params["after"] = after

            data = self._get(url, params)
            batch, after = parse_user_items(data)
            if not batch:
                break

            items.extend(batch)
            if not after:
                break

            self._sleep()

        return items[:limit]

    def get_subreddit_posts(
        self,
        subreddit: str,
        *,
        limit: int = 25,
        category: Category = Category.HOT,
        time_filter: TimeFilter = TimeFilter.ALL,
    ) -> list[SubredditPost]:
        """Fetch posts from a subreddit listing.

        Parameters
        ----------
        subreddit:
            Subreddit name (without ``r/`` prefix).
        limit:
            Maximum number of posts (paginated automatically).
        category:
            Listing category (hot, top, new, rising).
        time_filter:
            Time window for *top* listings.

        Returns
        -------
        list[SubredditPost]
        """
        url = f"{_BASE}/r/{subreddit}/{category.value}.json"
        return self._paginated_posts(url, limit, time_filter)

    def get_user_posts(
        self,
        username: str,
        *,
        limit: int = 25,
        category: UserCategory = UserCategory.NEW,
        time_filter: TimeFilter = TimeFilter.ALL,
    ) -> list[SubredditPost]:
        """Fetch a user's submitted posts.

        Parameters
        ----------
        username:
            Reddit username (without ``u/`` prefix).
        limit:
            Maximum number of posts.
        category:
            Listing category (hot, top, new).
        time_filter:
            Time window for *top* listings.

        Returns
        -------
        list[SubredditPost]
        """
        url = f"{_BASE}/user/{username}/submitted/{category.value}.json"
        return self._paginated_posts(url, limit, time_filter)

    def download_image(
        self,
        image_url: str,
        *,
        output_dir: str = "images",
    ) -> str:
        """Download an image from a Reddit post.

        Parameters
        ----------
        image_url:
            Direct URL to the image.
        output_dir:
            Directory to save the image.

        Returns
        -------
        str
            Path to the downloaded file.
        """
        filename = os.path.basename(urlparse(image_url).path) or "image.jpg"
        dest = os.path.join(output_dir, filename)
        return self._http.download(image_url, dest=dest)

    # ── Internal pagination ───────────────────────────────────────────────

    def _paginated_posts(
        self,
        url: str,
        limit: int,
        time_filter: TimeFilter,
    ) -> list[SubredditPost]:
        """Generic paginated listing fetcher."""
        posts: list[SubredditPost] = []
        after: str | None = None

        while len(posts) < limit:
            params: dict[str, Any] = {
                "limit": min(_BATCH_LIMIT, limit - len(posts)),
                "raw_json": 1,
                "t": time_filter.value,
            }
            if after:
                params["after"] = after

            data = self._get(url, params)
            batch, after = parse_subreddit_posts(data)
            if not batch:
                break

            posts.extend(batch)
            if not after:
                break

            self._sleep()

        return posts[:limit]
