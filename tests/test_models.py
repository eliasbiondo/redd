"""Unit tests for domain models and enumerations.

These tests verify the pure domain layer — no network calls.
"""

from __future__ import annotations

import pytest

from redd.domain.enums import Category, SortOrder, TimeFilter, UserCategory
from redd.domain.models import Comment, PostDetail, SearchResult, SubredditPost, UserItem

# ──────────────────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────────────────


class TestCategory:
    def test_values(self):
        assert Category.HOT.value == "hot"
        assert Category.TOP.value == "top"
        assert Category.NEW.value == "new"
        assert Category.RISING.value == "rising"

    def test_is_str_subclass(self):
        assert isinstance(Category.HOT, str)
        assert Category.HOT == "hot"


class TestUserCategory:
    def test_values(self):
        assert UserCategory.HOT.value == "hot"
        assert UserCategory.TOP.value == "top"
        assert UserCategory.NEW.value == "new"


class TestTimeFilter:
    def test_all_values_present(self):
        expected = {"hour", "day", "week", "month", "year", "all"}
        actual = {f.value for f in TimeFilter}
        assert actual == expected


class TestSortOrder:
    def test_all_values_present(self):
        expected = {"relevance", "hot", "top", "new", "comments"}
        actual = {s.value for s in SortOrder}
        assert actual == expected


# ──────────────────────────────────────────────────────────────────────────────
# Frozen dataclass behavior
# ──────────────────────────────────────────────────────────────────────────────


class TestSearchResult:
    def test_creation(self):
        result = SearchResult(
            title="Test",
            url="https://reddit.com/r/test/123",
            description="A test result",
            subreddit="test",
        )
        assert result.title == "Test"
        assert result.subreddit == "test"

    def test_immutability(self):
        result = SearchResult(title="T", url="u", description="d", subreddit="s")
        with pytest.raises(AttributeError):
            result.title = "Changed"  # type: ignore[misc]


class TestComment:
    def test_default_replies_empty(self):
        comment = Comment(author="user", body="hello", score=5)
        assert comment.replies == []

    def test_nested_replies(self):
        reply = Comment(author="replier", body="reply", score=2)
        parent = Comment(author="user", body="hello", score=5, replies=[reply])
        assert len(parent.replies) == 1
        assert parent.replies[0].author == "replier"


class TestPostDetail:
    def test_defaults(self):
        detail = PostDetail(
            title="P",
            author="a",
            body="b",
            score=1,
            url="u",
            subreddit="s",
            created_utc=0.0,
            num_comments=0,
        )
        assert detail.comments == []

    def test_with_comments(self):
        c = Comment(author="a", body="b", score=1)
        detail = PostDetail(
            title="P",
            author="a",
            body="b",
            score=1,
            url="u",
            subreddit="s",
            created_utc=0.0,
            num_comments=1,
            comments=[c],
        )
        assert len(detail.comments) == 1


class TestSubredditPost:
    def test_optional_fields_default_none(self):
        post = SubredditPost(
            title="T",
            author="a",
            permalink="/r/test/1",
            score=100,
            num_comments=5,
            created_utc=0.0,
            subreddit="test",
            url="https://reddit.com/r/test/1",
        )
        assert post.image_url is None
        assert post.thumbnail_url is None


class TestUserItem:
    def test_post_item(self):
        item = UserItem(kind="post", subreddit="test", url="u", created_utc=0.0, title="Title")
        assert item.title == "Title"
        assert item.body is None

    def test_comment_item(self):
        item = UserItem(kind="comment", subreddit="test", url="u", created_utc=0.0, body="Body")
        assert item.body == "Body"
        assert item.title is None
