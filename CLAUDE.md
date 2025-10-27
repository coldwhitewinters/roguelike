# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python roguelike game project built with the tcod library (libtcod Python bindings). The project is in early development stages with minimal implementation so far.

## Dependencies

- Python 3.12+
- tcod >= 16.0.0 (roguelike/terminal library for Python)
- uv (package manager - used for dependency management)

## Development Setup

The project uses **uv** for package management. uv.lock is tracked in version control for reproducible builds.

### Installing dependencies:
```bash
uv sync
```

### Running the application:
```bash
uv run python main.py
```

Or with uv's built-in shortcut:
```bash
uv run main.py
```

## Project Structure

Currently minimal structure:
- `main.py` - Entry point with basic "Hello from roguelike!" placeholder
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions

## Development Environment

The project includes a devcontainer configuration for consistent development environments:
- Python 3.12
- VS Code extensions: Python, Ruff (linting/formatting)
- Port 8000 forwarded (for potential web-based terminal or debug server)

## Code Quality

Ruff is configured as the linter and formatter (see devcontainer extensions). Use:
```bash
uvx ruff check .
uvx ruff format .
```

## Future Architecture Notes

Since this is a roguelike using tcod, expect the following architectural patterns to emerge:
- Game loop in main.py or dedicated game engine module
- Entity-Component-System (ECS) or entity hierarchy for game objects
- Map/dungeon generation systems
- Input handling and action processing
- Rendering system using tcod's console and tileset features
- Turn-based game state management
- Save/load functionality
