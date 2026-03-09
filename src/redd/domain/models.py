"""Domain models — immutable, framework-agnostic data containers."""

from __future__ import annotations

from dataclasses import dataclass, field

# ──────────────────────────────────────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class SearchResult:
    """A single search result from Reddit."""

    title: str
    url: str
    description: str
    subreddit: str


# ──────────────────────────────────────────────────────────────────────────────
# Posts & Comments
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Comment:
    """A single comment (or reply) with nested replies."""

    author: str
    body: str
    score: int
    replies: list[Comment] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class PostDetail:
    """Full details of a Reddit post, including its comment tree."""

    title: str
    author: str
    body: str
    score: int
    url: str
    subreddit: str
    created_utc: float
    num_comments: int
    comments: list[Comment] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# Subreddit listing
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class SubredditPost:
    """A post returned from a subreddit listing (hot/top/new/rising)."""

    title: str
    author: str
    permalink: str
    score: int
    num_comments: int
    created_utc: float
    subreddit: str
    url: str
    image_url: str | None = None
    thumbnail_url: str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# User data
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Post:
    """A user's submitted post."""

    title: str
    subreddit: str
    url: str
    created_utc: float


@dataclass(frozen=True, slots=True)
class UserItem:
    """A single item (post or comment) from a user's activity feed."""

    kind: str  # "post" | "comment"
    subreddit: str
    url: str
    created_utc: float
    title: str | None = None  # present on posts
    body: str | None = None  # present on comments
