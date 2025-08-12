# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python client library for the WordPress REST API. It provides both synchronous and asynchronous clients with full support for WordPress content types including posts, pages, categories, tags, users, media, and comments.

The library is built with:
- Python 3.11+
- FastAPI for web service integration
- Pydantic for data validation
- HTTPX and Requests for HTTP operations
- Poetry for dependency management

## Key Components

### Core Architecture
- `src/wp_python/core/`: Core client implementations (sync/async) and models
- `src/wp_python/service/`: Service classes for each WordPress content type
- `src/wp_python/utils/`: Utility functions and helpers
- `src/wp_python/plugin/`: Plugin system with FastAPI integration
- `examples/`: Usage examples for both sync and async operations

### Main Entry Points
- `WordPress` and `AsyncWordPress` classes in `src/wp_python/wordpress.py`
- Service classes like `PostService`, `CategoryService`, etc.
- Plugin system for FastAPI integration

## Development Commands

### Install Dependencies
```bash
poetry install
```

### Run Tests
```bash
poetry run pytest tests/
poetry run python -m pytest tests/
```

### Run Examples
```bash
poetry run python examples/basic_usage.py
```

## Code Structure

### Client Architecture
The library follows a service-oriented pattern:
1. Core HTTP clients (`WordPressClient`, `AsyncWordPressClient`) handle authentication and HTTP operations
2. Service classes (`PostService`, `CategoryService`, etc.) provide CRUD operations for each content type
3. Main `WordPress` and `AsyncWordPress` classes compose services and provide high-level API access

### Authentication
Multiple authentication methods supported:
- Basic authentication (username/password)
- Application passwords (recommended for production)
- JWT tokens (requires WordPress JWT plugin)
- Cookie authentication (nonce-based)

### Plugin System
Extensible plugin architecture with FastAPI integration:
- Base plugin class for custom extensions
- FastAPI plugin with automatic routing and middleware
- Support for Gunicorn + Uvicorn deployment

## Testing
Tests are written with pytest and cover:
- Model creation and validation
- Query builder functionality
- Client initialization and configuration
- Exception handling
- Basic integration scenarios

Run tests with: `poetry run pytest tests/`