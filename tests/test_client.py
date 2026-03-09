"""End-to-end tests for the sync Redd client.

These tests make real HTTP requests to Reddit's public JSON API.
They may be slow or flaky depending on network conditions and Reddit
rate-limiting. Mark them with ``pytest.mark.e2e`` for selective execution.
"""

from __future__ import annotations

import pytest

from redd import Category, Redd, SortOrder, TimeFilter
from redd.domain.models import PostDetail, SearchResult, SubredditPost, UserItem

pytestmark = pytest.mark.e2e


# ──────────────────────────────────────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────────────────────────────────────


class TestSearch:
    def test_global_search_returns_results(self, client: Redd):
        results = client.search("python", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 5
        for r in results:
            assert isinstance(r, SearchResult)
            assert r.title
            assert r.url.startswith("https://www.reddit.com")

    def test_search_respects_limit(self, client: Redd):
        results = client.search("programming", limit=3)
        assert len(results) <= 3

    def test_search_with_sort(self, client: Redd):
        results = client.search("linux", limit=3, sort=SortOrder.TOP)
        assert len(results) > 0

    def test_search_empty_query(self, client: Redd):
        results = client.search("asjdhaksjdhqwiueyhxznm", limit=3)
        # May return 0 or some results depending on Reddit
        assert isinstance(results, list)


# ──────────────────────────────────────────────────────────────────────────────
# Subreddit search
# ──────────────────────────────────────────────────────────────────────────────


class TestSearchSubreddit:
    def test_subreddit_search_returns_results(self, client: Redd):
        results = client.search_subreddit("python", "async", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, SearchResult)

    def test_subreddit_search_respects_limit(self, client: Redd):
        results = client.search_subreddit("programming", "rust", limit=2)
        assert len(results) <= 2


# ──────────────────────────────────────────────────────────────────────────────
# Subreddit posts
# ──────────────────────────────────────────────────────────────────────────────


class TestGetSubredditPosts:
    def test_fetch_hot_posts(self, client: Redd):
        posts = client.get_subreddit_posts("python", limit=5, category=Category.HOT)
        assert isinstance(posts, list)
        assert len(posts) > 0
        assert len(posts) <= 5
        for p in posts:
            assert isinstance(p, SubredditPost)
            assert p.title
            assert p.author
            assert p.subreddit.lower() == "python"

    def test_fetch_top_posts_with_time_filter(self, client: Redd):
        posts = client.get_subreddit_posts(
            "programming",
            limit=3,
            category=Category.TOP,
            time_filter=TimeFilter.MONTH,
        )
        assert len(posts) > 0
        for p in posts:
            assert isinstance(p, SubredditPost)
            assert p.score >= 0

    def test_fetch_new_posts(self, client: Redd):
        posts = client.get_subreddit_posts("all", limit=5, category=Category.NEW)
        assert len(posts) > 0

    def test_respects_limit(self, client: Redd):
        posts = client.get_subreddit_posts("python", limit=2)
        assert len(posts) <= 2

    def test_post_has_expected_fields(self, client: Redd):
        posts = client.get_subreddit_posts("python", limit=1)
        assert len(posts) == 1
        post = posts[0]
        assert isinstance(post.title, str)
        assert isinstance(post.author, str)
        assert isinstance(post.score, int)
        assert isinstance(post.num_comments, int)
        assert isinstance(post.created_utc, float)
        assert post.created_utc > 0


# ──────────────────────────────────────────────────────────────────────────────
# Post details
# ──────────────────────────────────────────────────────────────────────────────


class TestGetPost:
    def test_get_post_from_subreddit_listing(self, client: Redd):
        """Fetch a post from a listing, then scrape its full details."""
        posts = client.get_subreddit_posts("python", limit=1, category=Category.HOT)
        assert len(posts) > 0
        permalink = posts[0].permalink

        detail = client.get_post(permalink)
        assert isinstance(detail, PostDetail)
        assert detail.title
        assert detail.author
        assert isinstance(detail.score, int)
        assert isinstance(detail.comments, list)

    def test_post_comments_structure(self, client: Redd):
        """Verify comment tree structure on a post with comments."""
        posts = client.get_subreddit_posts(
            "AskReddit",
            limit=1,
            category=Category.HOT,
        )
        assert len(posts) > 0
        detail = client.get_post(posts[0].permalink)
        if detail.comments:
            comment = detail.comments[0]
            assert comment.author
            assert isinstance(comment.body, str)
            assert isinstance(comment.score, int)
            assert isinstance(comment.replies, list)


# ──────────────────────────────────────────────────────────────────────────────
# User data
# ──────────────────────────────────────────────────────────────────────────────


class TestGetUser:
    def test_fetch_user_activity(self, client: Redd):
        items = client.get_user("spez", limit=5)
        assert isinstance(items, list)
        assert len(items) > 0
        assert len(items) <= 5
        for item in items:
            assert isinstance(item, UserItem)
            assert item.kind in ("post", "comment")
            assert item.subreddit
            assert item.url.startswith("https://www.reddit.com")

    def test_user_posts_have_titles(self, client: Redd):
        items = client.get_user("spez", limit=20)
        posts = [i for i in items if i.kind == "post"]
        for p in posts:
            assert p.title is not None

    def test_user_comments_have_body(self, client: Redd):
        items = client.get_user("spez", limit=20)
        comments = [i for i in items if i.kind == "comment"]
        for c in comments:
            assert c.body is not None

    def test_respects_limit(self, client: Redd):
        items = client.get_user("spez", limit=3)
        assert len(items) <= 3


# ──────────────────────────────────────────────────────────────────────────────
# User submitted posts
# ──────────────────────────────────────────────────────────────────────────────


class TestGetUserPosts:
    def test_fetch_user_submitted(self, client: Redd):
        posts = client.get_user_posts("spez", limit=3)
        assert isinstance(posts, list)
        # spez may or may not have recent submitted posts
        for p in posts:
            assert isinstance(p, SubredditPost)


# ──────────────────────────────────────────────────────────────────────────────
# Context manager
# ──────────────────────────────────────────────────────────────────────────────


class TestContextManager:
    def test_with_statement(self):
        with Redd(throttle=(0, 0)) as r:
            results = r.search("test", limit=1)
            assert isinstance(results, list)
