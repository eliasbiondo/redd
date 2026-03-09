# Contributing to REDD

Thank you for your interest in contributing. This document explains how to set up
the project, run tests, and submit changes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up the Project](#setting-up-the-project)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Commit Guidelines](#commit-guidelines)
- [Submitting a Pull Request](#submitting-a-pull-request)

## Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setting Up the Project

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/<your-username>/redd.git
   cd redd
   ```

2. Install dependencies (including dev tools):

   ```bash
   uv sync
   ```

   This installs the package in editable mode along with `ruff`, `pytest`,
   `pytest-asyncio`, and `httpx`.

## Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/test_parsing.py
```

Run with verbose output:

```bash
uv run pytest -v
```

## Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and
formatting.

Lint (with auto-fix):

```bash
uv run ruff check --fix src/ tests/
```

Format:

```bash
uv run ruff format src/ tests/
```

Run both before committing:

```bash
uv run ruff check --fix src/ tests/ && uv run ruff format src/ tests/
```

## Commit Guidelines

- Use clear, concise commit messages.
- Use the imperative mood in the subject line (e.g., "Add search pagination"
  instead of "Added search pagination").
- Keep commits focused — one logical change per commit.

## Submitting a Pull Request

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all tests pass:

   ```bash
   uv run ruff check --fix src/ tests/
   uv run ruff format src/ tests/
   uv run pytest
   ```

3. Push your branch and open a pull request against `main`.

4. Describe your changes clearly in the PR description. Reference any related
   issues.

## Project Structure

```
src/redd/
├── __init__.py           # Public API surface
├── _client.py            # Sync client
├── _async_client.py      # Async client
├── _parsing.py           # JSON parsing (I/O-free)
├── _exceptions.py        # Error hierarchy
├── domain/               # Models and enums
├── ports/                # Abstract protocols
└── adapters/             # HTTP implementations

tests/
├── conftest.py           # Shared fixtures
├── test_models.py        # Domain model tests
├── test_parsing.py       # Parsing logic tests
└── test_client.py        # Client behavior tests
```

## Questions?

Open an issue or reach out at [contato@eliasbiondo.com](mailto:contato@eliasbiondo.com).
