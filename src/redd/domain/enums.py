"""Domain enumerations for Reddit data categories and filters."""

from __future__ import annotations

from enum import Enum


class Category(str, Enum):
    """Subreddit listing categories."""

    HOT = "hot"
    TOP = "top"
    NEW = "new"
    RISING = "rising"


class UserCategory(str, Enum):
    """User submitted-post listing categories."""

    HOT = "hot"
    TOP = "top"
    NEW = "new"


class TimeFilter(str, Enum):
    """Time window filter for top/controversial listings."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


class SortOrder(str, Enum):
    """Sort order for search results."""

    RELEVANCE = "relevance"
    HOT = "hot"
    TOP = "top"
    NEW = "new"
    COMMENTS = "comments"
