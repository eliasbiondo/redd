<div align="center">

# REDD

**Reddit Extraction and Data Dumper**

[![PyPI](https://img.shields.io/pypi/v/redd?label=pypi&cacheSeconds=3600)](https://pypi.org/project/redd/)
[![License: MIT](https://img.shields.io/github/license/eliasbiondo/redd?cacheSeconds=3600)](https://github.com/eliasbiondo/redd/blob/main/LICENSE)

A modern, async-ready Python library for extracting Reddit data.
No API keys required.

</div>

---

## Table of Contents

1. [Features](#1-features)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [API Reference](#4-api-reference)
5. [Architecture](#5-architecture)
6. [Examples](#6-examples)
7. [Contributing](#7-contributing)
8. [Disclaimer](#8-disclaimer)
9. [License](#9-license)

---

## 1. Features

- **No API keys** — uses Reddit's public `.json` endpoints.
- **Sync and async** — choose `Redd` or `AsyncRedd` depending on your stack.
- **Typed models** — frozen dataclasses instead of raw dictionaries.
- **Hexagonal architecture** — swap HTTP adapters without touching business logic.
- **Auto-pagination** — fetch hundreds of posts with a single call.
- **User-Agent rotation** — built-in rotation to reduce ban risk.
- **Proxy support** — pass a proxy URL and scrape at scale.
- **Throttling** — configurable random sleep between paginated requests.

---

## 2. Installation

With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv add redd
```

With pip:

```bash
pip install redd
```

For async support (requires [httpx](https://www.python-httpx.org/)):

```bash
uv add redd httpx
```

---

## 3. Quick Start

### 3.1. Synchronous usage

```python
from redd import Redd, Category, TimeFilter

with Redd() as r:
    # Search Reddit
    results = r.search("Python programming", limit=5)
    for item in results:
        print(f"  {item.title}")

    # Fetch top posts from a subreddit
    posts = r.get_subreddit_posts(
        "Python",
        limit=10,
        category=Category.TOP,
        time_filter=TimeFilter.WEEK,
    )
    for post in posts:
        print(f"  [{post.score:>5}] {post.title}")

    # Get full post details with comments
    detail = r.get_post("/r/Python/comments/abc123/example_post/")
    print(f"  {detail.title} -- {len(detail.comments)} comments")

    # Scrape user activity
    items = r.get_user("spez", limit=10)
    for item in items:
        print(f"  [{item.kind}] {item.title or item.body[:80]}")
```

### 3.2. Asynchronous usage

```python
import asyncio
from redd import AsyncRedd

async def main():
    async with AsyncRedd() as r:
        results = await r.search("machine learning", limit=5)
        for item in results:
            print(item.title)

asyncio.run(main())
```

### 3.3. Configuration

```python
r = Redd(
    proxy="http://user:pass@host:port",  # Optional proxy
    timeout=15.0,                        # Request timeout in seconds
    rotate_user_agent=True,              # Rotate UA per request
    throttle=(1.0, 3.0),                 # Random sleep range between pages
)
```

---

## 4. API Reference

### 4.1. Clients

| Class | Description |
|-------|-------------|
| `Redd` | Synchronous client (`requests`) |
| `AsyncRedd` | Asynchronous client (`httpx`) |

Both clients support context managers and expose the same API surface.

### 4.2. Methods

| Method | Description |
|--------|-------------|
| `search(query, *, limit, sort, after, before)` | Search all of Reddit |
| `search_subreddit(subreddit, query, *, limit, sort, after, before)` | Search within a subreddit |
| `get_post(permalink)` | Get full post details and comment tree |
| `get_user(username, *, limit)` | Get a user's recent activity |
| `get_subreddit_posts(subreddit, *, limit, category, time_filter)` | Fetch subreddit listings |
| `get_user_posts(username, *, limit, category, time_filter)` | Fetch a user's submitted posts |
| `download_image(image_url, *, output_dir)` | Download an image |
| `close()` | Release HTTP resources |

### 4.3. Models

All models are frozen dataclasses.

| Model | Fields |
|-------|--------|
| `SearchResult` | `title`, `url`, `description`, `subreddit` |
| `PostDetail` | `title`, `author`, `body`, `score`, `url`, `subreddit`, `created_utc`, `num_comments`, `comments` |
| `Comment` | `author`, `body`, `score`, `replies` |
| `SubredditPost` | `title`, `author`, `permalink`, `score`, `num_comments`, `created_utc`, `subreddit`, `url`, `image_url`, `thumbnail_url` |
| `UserItem` | `kind`, `subreddit`, `url`, `created_utc`, `title`, `body` |

### 4.4. Enums

| Enum | Values |
|------|--------|
| `Category` | `HOT`, `TOP`, `NEW`, `RISING` |
| `UserCategory` | `HOT`, `TOP`, `NEW` |
| `TimeFilter` | `HOUR`, `DAY`, `WEEK`, `MONTH`, `YEAR`, `ALL` |
| `SortOrder` | `RELEVANCE`, `HOT`, `TOP`, `NEW`, `COMMENTS` |

### 4.5. Exceptions

| Exception | Description |
|-----------|-------------|
| `ReddError` | Base exception for all REDD errors |
| `HttpError` | HTTP request failed after retries |
| `ParseError` | Reddit's JSON could not be parsed into domain models |
| `NotFoundError` | Requested resource does not exist |

---

## 5. Architecture

REDD follows hexagonal architecture (ports and adapters), separating business
logic from I/O concerns:

```mermaid
graph LR
    subgraph Public API
        A["Redd (sync)"]
        B["AsyncRedd (async)"]
    end

    subgraph Core
        C["Parsing Layer"]
        D["Domain Models"]
        E["Enums"]
    end

    subgraph Ports
        F["HttpPort"]
        G["AsyncHttpPort"]
    end

    subgraph Adapters
        H["RequestsHttpAdapter"]
        I["HttpxAsyncAdapter"]
    end

    A --> C
    B --> C
    C --> D
    C --> E
    A --> F
    B --> G
    F -.implements.-> H
    G -.implements.-> I
    H --> J["reddit.com"]
    I --> J
```

### Directory layout

```
src/redd/
├── __init__.py           # Public API surface
├── _client.py            # Sync client (Redd)
├── _async_client.py      # Async client (AsyncRedd)
├── _parsing.py           # JSON to domain model parsing (I/O-free)
├── _exceptions.py        # Error hierarchy
│
├── domain/               # Pure domain layer
│   ├── models.py         # Frozen dataclasses
│   └── enums.py          # Type-safe enumerations
│
├── ports/                # Abstract interfaces
│   └── http.py           # HttpPort and AsyncHttpPort protocols
│
└── adapters/             # Concrete implementations
    ├── http_sync.py      # requests-based adapter
    └── http_async.py     # httpx-based adapter
```

The parsing module has no I/O dependencies. Clients interact with the HTTP layer
exclusively through protocol-based ports, making it straightforward to swap
adapters, mock dependencies in tests, or add new transports.

---

## 6. Examples

See the [examples/](examples/) directory for runnable scripts.

**Fetch hot posts from a subreddit** ([subreddit_hot_posts.py](examples/subreddit_hot_posts.py)):

```python
from redd import Category, Redd

with Redd() as r:
    posts = r.get_subreddit_posts("brdev", limit=10, category=Category.HOT)

    for i, post in enumerate(posts, 1):
        print(f"{i:>2}. [{post.score:>5}] {post.title}")
        print(f"     by u/{post.author} — {post.num_comments} comments")
        print(f"     {post.url}")
        print()
```

Sample output:

```
 1. [   91] Qual o plano B de vocês caso a área piore muito?
     by u/Spiritual_Pangolin18 — 185 comments
     https://www.reddit.com/r/brdev/comments/1rnytuh/...

 2. [   83] Fuçando minhas coisas, encontrei um código de 600 linhas em Portugol
     by u/Dramatic-Revenue-802 — 7 comments
     https://www.reddit.com/r/brdev/comments/1ro269a/...
```

---

## 7. Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines on setting up the project, running tests, and submitting changes.

---

## 8. Disclaimer

Use responsibly. Reddit may rate-limit or ban IPs that make excessive requests.
Consider using rotating proxies for large-scale scraping.

---

## 9. License

MIT. See [LICENSE](LICENSE) for details.

Copyright (c) 2025 [Elias Biondo](mailto:contato@eliasbiondo.com)
