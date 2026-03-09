"""Shared JSON → domain-model parsing logic.

This module is framework-agnostic — it only transforms dicts into frozen
dataclasses. It has **no** dependency on ``requests``, ``httpx``, or any
I/O library, keeping the hexagonal boundary clean.
"""

from __future__ import annotations

import contextlib
import logging

from redd._exceptions import ParseError
from redd.domain.models import Comment, PostDetail, SearchResult, SubredditPost, UserItem

logger = logging.getLogger("redd.parsing")


# ──────────────────────────────────────────────────────────────────────────────
# Search results
# ──────────────────────────────────────────────────────────────────────────────


def parse_search_results(data: dict) -> list[SearchResult]:
    """Parse a Reddit search JSON response into a list of :class:`SearchResult`."""
    try:
        children = data["data"]["children"]
    except (KeyError, TypeError) as exc:
        raise ParseError("Unexpected search response structure") from exc

    results: list[SearchResult] = []
    for child in children:
        post = child.get("data", {})
        results.append(
            SearchResult(
                title=post.get("title", ""),
                url=f"https://www.reddit.com{post.get('permalink', '')}",
                description=post.get("selftext", "")[:500],
                subreddit=post.get("subreddit", ""),
            )
        )
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Post details
# ──────────────────────────────────────────────────────────────────────────────


def parse_post_detail(data: list | dict) -> PostDetail:
    """Parse a Reddit post JSON response into a :class:`PostDetail`."""
    if not isinstance(data, list) or len(data) < 2:
        raise ParseError("Unexpected post data structure — expected a list with ≥ 2 elements")

    try:
        main = data[0]["data"]["children"][0]["data"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ParseError("Failed to extract main post data") from exc

    comments = _parse_comments(data[1].get("data", {}).get("children", []))

    return PostDetail(
        title=main.get("title", ""),
        author=main.get("author", ""),
        body=main.get("selftext", ""),
        score=main.get("score", 0),
        url=f"https://www.reddit.com{main.get('permalink', '')}",
        subreddit=main.get("subreddit", ""),
        created_utc=main.get("created_utc", 0.0),
        num_comments=main.get("num_comments", 0),
        comments=comments,
    )


def _parse_comments(children: list) -> list[Comment]:
    """Recursively parse a Reddit comment tree."""
    comments: list[Comment] = []
    for child in children:
        if not isinstance(child, dict) or child.get("kind") != "t1":
            continue

        cdata = child.get("data", {})
        replies_raw = cdata.get("replies", "")
        nested: list[Comment] = []
        if isinstance(replies_raw, dict):
            nested = _parse_comments(replies_raw.get("data", {}).get("children", []))

        comments.append(
            Comment(
                author=cdata.get("author", ""),
                body=cdata.get("body", ""),
                score=cdata.get("score", 0),
                replies=nested,
            )
        )
    return comments


# ──────────────────────────────────────────────────────────────────────────────
# Subreddit listing
# ──────────────────────────────────────────────────────────────────────────────


def parse_subreddit_posts(data: dict) -> tuple[list[SubredditPost], str | None]:
    """Parse a subreddit listing and return ``(posts, after_cursor)``."""
    try:
        children = data["data"]["children"]
        after = data["data"].get("after")
    except (KeyError, TypeError) as exc:
        raise ParseError("Unexpected subreddit listing structure") from exc

    posts: list[SubredditPost] = []
    for child in children:
        p = child.get("data", {})

        image_url: str | None = None
        if p.get("post_hint") == "image" and "url" in p:
            image_url = p["url"]
        elif "preview" in p and "images" in p.get("preview", {}):
            with contextlib.suppress(KeyError, IndexError):
                image_url = p["preview"]["images"][0]["source"]["url"]

        thumbnail_url: str | None = None
        thumb = p.get("thumbnail", "")
        if thumb and thumb not in ("self", "default", "nsfw", "spoiler", "image"):
            thumbnail_url = thumb

        posts.append(
            SubredditPost(
                title=p.get("title", ""),
                author=p.get("author", ""),
                permalink=p.get("permalink", ""),
                score=p.get("score", 0),
                num_comments=p.get("num_comments", 0),
                created_utc=p.get("created_utc", 0.0),
                subreddit=p.get("subreddit", ""),
                url=f"https://www.reddit.com{p.get('permalink', '')}",
                image_url=image_url,
                thumbnail_url=thumbnail_url,
            )
        )
    return posts, after


# ──────────────────────────────────────────────────────────────────────────────
# User activity
# ──────────────────────────────────────────────────────────────────────────────


def parse_user_items(data: dict) -> tuple[list[UserItem], str | None]:
    """Parse a user activity listing and return ``(items, after_cursor)``."""
    try:
        children = data["data"]["children"]
        after = data["data"].get("after")
    except (KeyError, TypeError) as exc:
        raise ParseError("Unexpected user data structure") from exc

    items: list[UserItem] = []
    for child in children:
        kind = child.get("kind", "")
        d = child.get("data", {})
        permalink = d.get("permalink", "")
        url = f"https://www.reddit.com{permalink}"

        if kind == "t3":  # post
            items.append(
                UserItem(
                    kind="post",
                    subreddit=d.get("subreddit", ""),
                    url=url,
                    created_utc=d.get("created_utc", 0.0),
                    title=d.get("title", ""),
                )
            )
        elif kind == "t1":  # comment
            items.append(
                UserItem(
                    kind="comment",
                    subreddit=d.get("subreddit", ""),
                    url=url,
                    created_utc=d.get("created_utc", 0.0),
                    body=d.get("body", ""),
                )
            )
    return items, after
