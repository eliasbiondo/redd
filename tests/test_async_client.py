"""End-to-end tests for the async AsyncRedd client.

These tests make real HTTP requests to Reddit's public JSON API.
"""

from __future__ import annotations

import pytest

from redd import AsyncRedd, Category, SortOrder, TimeFilter
from redd.domain.models import PostDetail, SearchResult, SubredditPost, UserItem

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ──────────────────────────────────────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────────────────────────────────────


class TestAsyncSearch:
    async def test_global_search(self, async_client: AsyncRedd):
        results = await async_client.search("python", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 5
        for r in results:
            assert isinstance(r, SearchResult)
            assert r.title

    async def test_search_with_sort(self, async_client: AsyncRedd):
        results = await async_client.search("linux", limit=3, sort=SortOrder.TOP)
        assert len(results) > 0

    async def test_subreddit_search(self, async_client: AsyncRedd):
        results = await async_client.search_subreddit("python", "async", limit=3)
        assert isinstance(results, list)
        assert len(results) > 0


# ──────────────────────────────────────────────────────────────────────────────
# Subreddit posts
# ──────────────────────────────────────────────────────────────────────────────


class TestAsyncSubredditPosts:
    async def test_fetch_hot(self, async_client: AsyncRedd):
        posts = await async_client.get_subreddit_posts("python", limit=5, category=Category.HOT)
        assert len(posts) > 0
        assert len(posts) <= 5
        for p in posts:
            assert isinstance(p, SubredditPost)

    async def test_fetch_top_with_filter(self, async_client: AsyncRedd):
        posts = await async_client.get_subreddit_posts(
            "programming",
            limit=3,
            category=Category.TOP,
            time_filter=TimeFilter.WEEK,
        )
        assert len(posts) > 0

    async def test_respects_limit(self, async_client: AsyncRedd):
        posts = await async_client.get_subreddit_posts("python", limit=2)
        assert len(posts) <= 2


# ──────────────────────────────────────────────────────────────────────────────
# Post details
# ──────────────────────────────────────────────────────────────────────────────


class TestAsyncPostDetail:
    async def test_get_post(self, async_client: AsyncRedd):
        posts = await async_client.get_subreddit_posts("python", limit=1)
        assert len(posts) > 0

        detail = await async_client.get_post(posts[0].permalink)
        assert isinstance(detail, PostDetail)
        assert detail.title
        assert isinstance(detail.comments, list)


# ──────────────────────────────────────────────────────────────────────────────
# User data
# ──────────────────────────────────────────────────────────────────────────────


class TestAsyncUserData:
    async def test_fetch_user_activity(self, async_client: AsyncRedd):
        items = await async_client.get_user("spez", limit=5)
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, UserItem)
            assert item.kind in ("post", "comment")

    async def test_respects_limit(self, async_client: AsyncRedd):
        items = await async_client.get_user("spez", limit=3)
        assert len(items) <= 3


# ──────────────────────────────────────────────────────────────────────────────
# Context manager
# ──────────────────────────────────────────────────────────────────────────────


class TestAsyncContextManager:
    async def test_async_with_statement(self):
        async with AsyncRedd(throttle=(0, 0)) as r:
            results = await r.search("test", limit=1)
            assert isinstance(results, list)
