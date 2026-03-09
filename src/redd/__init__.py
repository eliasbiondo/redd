"""
REDD — Reddit Extraction and Data Dumper
========================================

A modern, async-ready Python library for extracting Reddit data
without API keys.

Quick start (sync)::

    from redd import Redd

    with Redd() as r:
        posts = r.get_subreddit_posts("Python", limit=10)
        for p in posts:
            print(p.title, p.score)

Quick start (async)::

    import asyncio
    from redd import AsyncRedd

    async def main():
        async with AsyncRedd() as r:
            results = await r.search("machine learning", limit=5)
            for item in results:
                print(item.title)

    asyncio.run(main())
"""

from redd._async_client import AsyncRedd
from redd._client import Redd
from redd._exceptions import HttpError, NotFoundError, ParseError, ReddError
from redd._version import __version__
from redd.domain.enums import Category, SortOrder, TimeFilter, UserCategory
from redd.domain.models import (
    Comment,
    Post,
    PostDetail,
    SearchResult,
    SubredditPost,
    UserItem,
)

__all__ = [
    "AsyncRedd",
    "Category",
    "Comment",
    "HttpError",
    "NotFoundError",
    "ParseError",
    "Post",
    "PostDetail",
    "Redd",
    "ReddError",
    "SearchResult",
    "SortOrder",
    "SubredditPost",
    "TimeFilter",
    "UserCategory",
    "UserItem",
    "__version__",
]
