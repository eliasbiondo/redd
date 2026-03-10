#!/usr/bin/env python3
"""
REDD Terminal Demo
==================

An interactive, cinematic terminal demo showcasing REDD's capabilities.
Designed for recording (asciinema/terminalizer) and posting to Reddit.

Usage:
    uv run python examples/demo.py
    uv run python examples/demo.py --fast # Skip pauses
    uv run python examples/demo.py --subreddit Python
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from textwrap import shorten

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from redd import Category, Redd, TimeFilter

# ── Palette ───────────────────────────────────────────────────────────────────

ORANGE = "#FF4500"
DARK_ORANGE = "#CC3700"
LIGHT_GRAY = "#C0C0C0"
MUTED = "#888888"
WHITE = "#FFFFFF"
UPVOTE = "#FF8B60"
COMMENT_BLUE = "#5B9BD5"
GREEN = "#77DD77"
GOLD = "#FFD700"

console = Console(highlight=False)

# ── Helpers ───────────────────────────────────────────────────────────────────


def pause(seconds: float, fast: bool = False) -> None:
    """Sleep unless running in --fast mode."""
    if not fast:
        time.sleep(seconds)


def typewriter(text: str, style: str = "", *, fast: bool = False) -> None:
    """Print text character by character for a typewriter effect."""
    if fast:
        console.print(text, style=style)
        return
    rendered = Text(text, style=style)
    for i in range(len(text)):
        console.print(Text(text[: i + 1], style=style), end="\r")
        time.sleep(0.02)
    console.print(rendered)


def section_transition(fast: bool = False) -> None:
    console.print()
    console.print(Rule(style=MUTED))
    console.print()
    pause(0.6, fast)


def relative_time(utc_timestamp: float) -> str:
    """Convert a UTC timestamp to a human-readable relative time."""
    now = datetime.now(timezone.utc)
    dt = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    return f"{months}mo ago"


def format_score(score: int) -> Text:
    """Format a score with color based on magnitude."""
    if score >= 1000:
        txt = f"▲ {score:,}"
        return Text(txt, style=f"bold {GOLD}")
    elif score >= 100:
        txt = f"▲ {score:,}"
        return Text(txt, style=f"bold {UPVOTE}")
    elif score > 0:
        txt = f"▲ {score}"
        return Text(txt, style=UPVOTE)
    else:
        txt = f"▼ {score}"
        return Text(txt, style="dim red")


# ── Sections ──────────────────────────────────────────────────────────────────


def show_banner(fast: bool = False) -> None:
    """Animated intro banner."""

    logo = r"""
    ██████╗ ███████╗██████╗ ██████╗
    ██╔══██╗██╔════╝██╔══██╗██╔══██╗
    ██████╔╝█████╗  ██║  ██║██║  ██║
    ██╔══██╗██╔══╝  ██║  ██║██║  ██║
    ██║  ██║███████╗██████╔╝██████╔╝
    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝
    """

    logo_text = Text(logo, style=f"bold {ORANGE}")
    console.print(Align.center(logo_text))
    pause(0.4, fast)

    tagline = Text(
        "Reddit Extraction and Data Dumper",
        style=f"italic {LIGHT_GRAY}",
    )
    console.print(Align.center(tagline))
    pause(0.2, fast)

    subtitle = Text(
        "No API keys · Sync & Async · Typed models · Auto-pagination",
        style=f"dim {MUTED}",
    )
    console.print(Align.center(subtitle))
    console.print()
    pause(0.8, fast)

    # Install badge
    install_panel = Panel(
        Align.center(Text("uv add redd", style=f"bold {GREEN}")),
        border_style=Style(color=ORANGE),
        padding=(0, 2),
        expand=False,
    )
    console.print(Align.center(install_panel))
    pause(1.0, fast)


def show_search(fast: bool = False) -> None:
    """Search Reddit demo."""
    section_transition(fast)

    typewriter("🔍  Searching Reddit...", style=f"bold {WHITE}", fast=fast)
    console.print()
    pause(0.3, fast)

    cmd = Text('>>> r.search("python web scraping", limit=5)', style=f"bold {GREEN}")
    console.print(cmd)
    console.print()
    pause(0.4, fast)

    with (
        console.status(
            "[bold]Fetching results...",
            spinner="dots",
            spinner_style=ORANGE,
        ),
        Redd(throttle=(0, 0)) as r,
    ):
        results = r.search("python web scraping", limit=5)

    table = Table(
        title="Search Results",
        title_style=f"bold {ORANGE}",
        box=box.ROUNDED,
        border_style=MUTED,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style=f"bold {ORANGE}", width=3, justify="center")
    table.add_column("Title", style=WHITE, max_width=55)
    table.add_column("Subreddit", style=COMMENT_BLUE, width=18, justify="center")

    for i, result in enumerate(results, 1):
        table.add_row(
            str(i),
            shorten(result.title, width=55, placeholder="…"),
            f"r/{result.subreddit}",
        )

    console.print(table)
    pause(1.5, fast)


def show_subreddit(subreddit: str, fast: bool = False) -> list:
    """Subreddit hot posts demo."""
    section_transition(fast)

    typewriter(
        f"🔥  Browsing r/{subreddit} — Hot posts",
        style=f"bold {WHITE}",
        fast=fast,
    )
    console.print()
    pause(0.3, fast)

    cmd = Text(
        f'>>> r.get_subreddit_posts("{subreddit}", limit=8, category=Category.HOT)',
        style=f"bold {GREEN}",
    )
    console.print(cmd)
    console.print()
    pause(0.4, fast)

    with (
        console.status(
            f"[bold]Loading r/{subreddit}...",
            spinner="dots",
            spinner_style=ORANGE,
        ),
        Redd(throttle=(0, 0)) as r,
    ):
        posts = r.get_subreddit_posts(subreddit, limit=8, category=Category.HOT)

    table = Table(
        title=f"r/{subreddit} · Hot",
        title_style=f"bold {ORANGE}",
        box=box.ROUNDED,
        border_style=MUTED,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Score", width=10, justify="center")
    table.add_column("Title", style=WHITE, max_width=50)
    table.add_column("Author", style=COMMENT_BLUE, width=18)
    table.add_column("💬", width=5, justify="right", style=MUTED)
    table.add_column("⏱", width=8, justify="right", style=MUTED)

    for post in posts:
        table.add_row(
            format_score(post.score),
            shorten(post.title, width=50, placeholder="…"),
            f"u/{post.author}",
            str(post.num_comments),
            relative_time(post.created_utc),
        )

    console.print(table)
    pause(1.5, fast)
    return posts


def show_post_detail(posts: list, fast: bool = False) -> None:
    """Post detail with comment tree demo."""
    section_transition(fast)

    # Pick first non-pinned post with comments
    target = None
    for p in posts:
        if p.num_comments > 0 and p.score > 0:
            target = p
            break
    if not target:
        target = posts[0] if posts else None

    if not target:
        console.print("[dim]No posts available for detail view.[/dim]")
        return

    typewriter(
        "📖  Diving into a post...",
        style=f"bold {WHITE}",
        fast=fast,
    )
    console.print()
    pause(0.3, fast)

    cmd = Text(
        f'>>> r.get_post("{shorten(target.permalink, width=50, placeholder="…")}")',
        style=f"bold {GREEN}",
    )
    console.print(cmd)
    console.print()
    pause(0.4, fast)

    with (
        console.status(
            "[bold]Loading post & comments...",
            spinner="dots",
            spinner_style=ORANGE,
        ),
        Redd(throttle=(0, 0)) as r,
    ):
        detail = r.get_post(target.permalink)

    # Post header panel
    header_parts = [
        Text(detail.title, style=f"bold {WHITE}"),
        Text(f"\nby u/{detail.author}", style=COMMENT_BLUE),
        Text(f"  ·  r/{detail.subreddit}", style=MUTED),
        Text("  ·  ", style=MUTED),
        format_score(detail.score),
        Text(f"  ·  💬 {detail.num_comments}", style=MUTED),
    ]
    header = Text()
    for part in header_parts:
        header.append(part)

    if detail.body and detail.body.strip():
        body_preview = shorten(detail.body.strip(), width=300, placeholder="…")
        header.append(Text(f"\n\n{body_preview}", style=LIGHT_GRAY))

    console.print(
        Panel(
            header,
            border_style=Style(color=ORANGE),
            padding=(1, 2),
            title="[bold]Post Detail[/bold]",
            title_align="left",
        )
    )
    pause(0.8, fast)

    # Comment tree
    if detail.comments:
        console.print()
        typewriter(
            f"💬  Comment tree ({min(len(detail.comments), 5)} top-level):",
            style=f"bold {WHITE}",
            fast=fast,
        )
        console.print()
        pause(0.3, fast)

        tree = Tree(
            Text("Comments", style=f"bold {ORANGE}"),
            guide_style=MUTED,
        )

        def add_comments(parent_tree, comments, depth=0, max_depth=2):
            for comment in comments[:5]:  # Show up to 5 at each level
                score_str = f"▲{comment.score}" if comment.score >= 0 else f"▼{comment.score}"
                body_preview = shorten(
                    comment.body.replace("\n", " ").strip(),
                    width=70,
                    placeholder="…",
                )

                label = Text()
                label.append(f"u/{comment.author} ", style=COMMENT_BLUE)
                label.append(f"({score_str}) ", style=UPVOTE if comment.score >= 0 else "dim red")
                label.append(body_preview, style=LIGHT_GRAY)

                node = parent_tree.add(label)

                if comment.replies and depth < max_depth:
                    add_comments(node, comment.replies, depth + 1, max_depth)

        add_comments(tree, detail.comments)
        console.print(tree)
    pause(1.2, fast)


def show_user(fast: bool = False) -> None:
    """User activity demo."""
    section_transition(fast)

    username = "spez"
    typewriter(
        f"👤  Stalking u/{username}'s activity...",
        style=f"bold {WHITE}",
        fast=fast,
    )
    console.print()
    pause(0.3, fast)

    cmd = Text(
        f'>>> r.get_user("{username}", limit=5)',
        style=f"bold {GREEN}",
    )
    console.print(cmd)
    console.print()
    pause(0.4, fast)

    with (
        console.status(
            f"[bold]Loading u/{username}...",
            spinner="dots",
            spinner_style=ORANGE,
        ),
        Redd(throttle=(0, 0)) as r,
    ):
        items = r.get_user(username, limit=5)

    if not items:
        console.print(f"[dim]No public activity found for u/{username}.[/dim]")
        return

    for item in items:
        kind_badge = (
            Text(" POST ", style="bold white on #FF4500")
            if item.kind == "post"
            else Text(" COMMENT ", style="bold white on #5B9BD5")
        )

        content = item.title or (shorten(item.body or "", width=80, placeholder="…"))
        sub = Text(f"r/{item.subreddit}", style=COMMENT_BLUE)
        stamp = Text(f" · {relative_time(item.created_utc)}", style=MUTED)

        line = Text()
        line.append(kind_badge)
        line.append(" ")
        line.append(sub)
        line.append(stamp)

        console.print(line)
        console.print(f"  {content}", style=LIGHT_GRAY)
        console.print()
        pause(0.3, fast)

    pause(0.5, fast)


def show_top_posts(subreddit: str, fast: bool = False) -> None:
    """Show top posts of all time as a second listing demo."""
    section_transition(fast)

    typewriter(
        f"🏆  Top posts of all time from r/{subreddit}",
        style=f"bold {WHITE}",
        fast=fast,
    )
    console.print()
    pause(0.3, fast)

    cmd = Text(
        f'>>> r.get_subreddit_posts("{subreddit}", limit=5, category=Category.TOP, time_filter=TimeFilter.ALL)',
        style=f"bold {GREEN}",
    )
    console.print(cmd)
    console.print()
    pause(0.4, fast)

    with (
        console.status(
            "[bold]Loading top posts...",
            spinner="dots",
            spinner_style=ORANGE,
        ),
        Redd(throttle=(0, 0)) as r,
    ):
        posts = r.get_subreddit_posts(
            subreddit,
            limit=5,
            category=Category.TOP,
            time_filter=TimeFilter.ALL,
        )

    for i, post in enumerate(posts, 1):
        rank = Text(f" #{i} ", style=f"bold white on {DARK_ORANGE}")
        title = Text(f" {shorten(post.title, width=60, placeholder='…')}", style=f"bold {WHITE}")
        meta = Text(
            f"  {post.score:,} pts · 💬 {post.num_comments} · u/{post.author}",
            style=MUTED,
        )

        line = Text()
        line.append(rank)
        line.append(title)
        console.print(line)
        console.print(f"   {meta}")
        console.print()
        pause(0.4, fast)

    pause(0.5, fast)


def show_outro(fast: bool = False) -> None:
    """Closing credits."""
    section_transition(fast)

    # Feature summary
    features = [
        "✦ No API keys needed",
        "✦ Sync & Async clients",
        "✦ Typed dataclass models",
        "✦ Auto-pagination",
        "✦ User-Agent rotation",
        "✦ Proxy support",
    ]

    cols = Columns(
        [Text(f, style=LIGHT_GRAY) for f in features],
        equal=True,
        expand=True,
    )

    outro_panel = Panel(
        Align.center(cols),
        border_style=Style(color=ORANGE),
        title=f"[bold {ORANGE}]✨ REDD — Features[/]",
        padding=(1, 2),
    )
    console.print(outro_panel)
    console.print()
    pause(0.5, fast)

    # Install + links
    install_text = Text(justify="center")
    install_text.append("uv add redd", style=f"bold {GREEN}")
    install_text.append("\n\n")
    install_text.append("github.com/eliasbiondo/redd", style=f"dim {COMMENT_BLUE}")
    install = Panel(
        Align.center(install_text),
        border_style=Style(color=MUTED),
        padding=(1, 3),
        expand=False,
    )
    console.print(Align.center(install))
    console.print()

    # Star CTA
    cta_text = Text(justify="center")
    cta_text.append("Did you like it? ", style=f"{WHITE}")
    cta_text.append("Give us a \u2b50!", style=f"bold {GOLD}")
    cta_text.append("\n")
    cta_text.append("github.com/eliasbiondo/redd", style=f"dim {COMMENT_BLUE}")
    cta = Panel(
        Align.center(cta_text),
        border_style=Style(color=GOLD),
        padding=(1, 3),
        expand=False,
    )
    console.print(Align.center(cta))
    console.print()

    thanks = Text("Thanks! 🚀", style=f"bold {ORANGE}")
    console.print(Align.center(thanks))
    console.print()


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="REDD terminal demo")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip all pauses (for testing, not recording)",
    )
    parser.add_argument(
        "--subreddit",
        default="Python",
        help="Subreddit to feature in the demo (default: Python)",
    )
    args = parser.parse_args()

    fast = args.fast
    subreddit = args.subreddit

    console.clear()
    pause(0.5, fast)

    try:
        show_banner(fast)
        show_search(fast)
        posts = show_subreddit(subreddit, fast)
        show_post_detail(posts, fast)
        show_user(fast)
        show_top_posts(subreddit, fast)
        show_outro(fast)
    except KeyboardInterrupt:
        console.print("\n[dim]Demo interrupted.[/dim]")
        sys.exit(0)
    except Exception as exc:
        console.print(f"\n[bold red]Error:[/bold red] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
