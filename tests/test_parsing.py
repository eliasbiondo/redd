"""Unit tests for the parsing module.

These tests use fixture data (no network calls) and run in CI.
"""

from __future__ import annotations

import pytest

from redd._exceptions import ParseError
from redd._parsing import (
    parse_post_detail,
    parse_search_results,
    parse_subreddit_posts,
    parse_user_items,
)

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


def _search_response(count: int = 3) -> dict:
    children = []
    for i in range(count):
        children.append(
            {
                "kind": "t3",
                "data": {
                    "title": f"Post {i}",
                    "permalink": f"/r/test/comments/id{i}/post_{i}/",
                    "selftext": f"Body {i}. " * 10,
                    "subreddit": "test",
                    "score": (i + 1) * 100,
                    "author": f"user_{i}",
                    "created_utc": 1700000000.0 + i,
                    "num_comments": i * 5,
                },
            }
        )
    return {"data": {"children": children, "after": "t3_next", "before": None}}


def _post_detail_response(num_comments: int = 2) -> list:
    comments = []
    for i in range(num_comments):
        comments.append(
            {
                "kind": "t1",
                "data": {
                    "author": f"commenter_{i}",
                    "body": f"Comment {i}.",
                    "score": (i + 1) * 10,
                    "replies": "",
                },
            }
        )
    return [
        {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Test Post",
                            "author": "author",
                            "selftext": "Body text.",
                            "score": 1500,
                            "permalink": "/r/test/comments/xyz/test_post/",
                            "subreddit": "test",
                            "created_utc": 1700000000.0,
                            "num_comments": num_comments,
                        },
                    }
                ],
            },
        },
        {"data": {"children": comments}},
    ]


def _nested_comments_response() -> list:
    return [
        {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Nested Post",
                            "author": "op",
                            "selftext": "Body.",
                            "score": 500,
                            "permalink": "/r/test/comments/nest/nested_post/",
                            "subreddit": "test",
                            "created_utc": 1700000000.0,
                            "num_comments": 3,
                        },
                    }
                ],
            },
        },
        {
            "data": {
                "children": [
                    {
                        "kind": "t1",
                        "data": {
                            "author": "parent",
                            "body": "Top-level.",
                            "score": 50,
                            "replies": {
                                "data": {
                                    "children": [
                                        {
                                            "kind": "t1",
                                            "data": {
                                                "author": "child",
                                                "body": "Reply.",
                                                "score": 20,
                                                "replies": "",
                                            },
                                        }
                                    ],
                                },
                            },
                        },
                    },
                    {
                        "kind": "more",
                        "data": {"count": 5, "children": ["a", "b"]},
                    },
                ],
            },
        },
    ]


def _subreddit_listing(count: int = 3, after: str | None = None) -> dict:
    children = []
    for i in range(count):
        children.append(
            {
                "kind": "t3",
                "data": {
                    "title": f"Sub Post {i}",
                    "author": f"author_{i}",
                    "permalink": f"/r/test/comments/s{i}/sub_post_{i}/",
                    "score": (i + 1) * 200,
                    "num_comments": (i + 1) * 3,
                    "created_utc": 1700000000.0 + i * 3600,
                    "subreddit": "test",
                    "post_hint": "image" if i == 0 else "self",
                    "url": f"https://i.redd.it/img{i}.jpg" if i == 0 else f"https://reddit.com/{i}",
                    "thumbnail": "https://thumb.example.com/t.jpg" if i == 1 else "self",
                },
            }
        )
    return {"data": {"children": children, "after": after}}


def _user_activity(num_posts: int = 1, num_comments: int = 1, after: str | None = None) -> dict:
    children = []
    for i in range(num_posts):
        children.append(
            {
                "kind": "t3",
                "data": {
                    "title": f"User Post {i}",
                    "subreddit": "test",
                    "permalink": f"/r/test/comments/up{i}/user_post_{i}/",
                    "created_utc": 1700000000.0 + i,
                },
            }
        )
    for i in range(num_comments):
        children.append(
            {
                "kind": "t1",
                "data": {
                    "body": f"User comment {i}.",
                    "subreddit": "askreddit",
                    "permalink": f"/r/askreddit/comments/uc{i}/thread/c{i}/",
                    "created_utc": 1700000000.0 + num_posts + i,
                },
            }
        )
    return {"data": {"children": children, "after": after}}


# ──────────────────────────────────────────────────────────────────────────────
# Search parsing
# ──────────────────────────────────────────────────────────────────────────────


class TestParseSearchResults:
    def test_basic(self):
        results = parse_search_results(_search_response(3))
        assert len(results) == 3
        assert results[0].title == "Post 0"
        assert results[0].subreddit == "test"
        assert "/r/test/comments/id0/" in results[0].url

    def test_empty(self):
        results = parse_search_results({"data": {"children": []}})
        assert results == []

    def test_description_truncated_at_500(self):
        data = _search_response(1)
        data["data"]["children"][0]["data"]["selftext"] = "x" * 1000
        results = parse_search_results(data)
        assert len(results[0].description) <= 500

    def test_invalid_structure(self):
        with pytest.raises(ParseError):
            parse_search_results({"bad": "data"})

    def test_none_raises(self):
        with pytest.raises(ParseError):
            parse_search_results(None)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# Post detail parsing
# ──────────────────────────────────────────────────────────────────────────────


class TestParsePostDetail:
    def test_basic(self):
        detail = parse_post_detail(_post_detail_response(2))
        assert detail.title == "Test Post"
        assert detail.author == "author"
        assert detail.score == 1500
        assert len(detail.comments) == 2
        assert detail.comments[0].author == "commenter_0"

    def test_nested_comments(self):
        detail = parse_post_detail(_nested_comments_response())
        assert len(detail.comments) == 1
        parent = detail.comments[0]
        assert parent.author == "parent"
        assert len(parent.replies) == 1
        assert parent.replies[0].author == "child"
        assert parent.replies[0].body == "Reply."

    def test_no_comments(self):
        detail = parse_post_detail(_post_detail_response(0))
        assert detail.comments == []

    def test_dict_raises(self):
        with pytest.raises(ParseError):
            parse_post_detail({"not": "a list"})

    def test_short_list_raises(self):
        with pytest.raises(ParseError):
            parse_post_detail([{"data": {}}])


# ──────────────────────────────────────────────────────────────────────────────
# Subreddit listing parsing
# ──────────────────────────────────────────────────────────────────────────────


class TestParseSubredditPosts:
    def test_basic(self):
        posts, after = parse_subreddit_posts(_subreddit_listing(3, after="next"))
        assert len(posts) == 3
        assert after == "next"
        assert posts[0].title == "Sub Post 0"

    def test_image_url(self):
        posts, _ = parse_subreddit_posts(_subreddit_listing(3))
        assert posts[0].image_url == "https://i.redd.it/img0.jpg"
        assert posts[1].image_url is None

    def test_thumbnail(self):
        posts, _ = parse_subreddit_posts(_subreddit_listing(3))
        assert posts[1].thumbnail_url == "https://thumb.example.com/t.jpg"
        assert posts[0].thumbnail_url is None  # "self" is filtered out

    def test_no_after(self):
        _, after = parse_subreddit_posts(_subreddit_listing(2, after=None))
        assert after is None

    def test_empty(self):
        posts, after = parse_subreddit_posts({"data": {"children": [], "after": None}})
        assert posts == []
        assert after is None

    def test_invalid_structure(self):
        with pytest.raises(ParseError):
            parse_subreddit_posts({"invalid": True})


# ──────────────────────────────────────────────────────────────────────────────
# User activity parsing
# ──────────────────────────────────────────────────────────────────────────────


class TestParseUserItems:
    def test_mixed(self):
        items, after = parse_user_items(_user_activity(2, 1, after="next"))
        assert len(items) == 3
        assert after == "next"
        assert sum(1 for i in items if i.kind == "post") == 2
        assert sum(1 for i in items if i.kind == "comment") == 1

    def test_post_fields(self):
        items, _ = parse_user_items(_user_activity(1, 0))
        assert items[0].kind == "post"
        assert items[0].title == "User Post 0"
        assert items[0].body is None

    def test_comment_fields(self):
        items, _ = parse_user_items(_user_activity(0, 1))
        assert items[0].kind == "comment"
        assert items[0].body == "User comment 0."
        assert items[0].title is None

    def test_empty(self):
        items, after = parse_user_items({"data": {"children": [], "after": None}})
        assert items == []
        assert after is None

    def test_invalid_structure(self):
        with pytest.raises(ParseError):
            parse_user_items({})
