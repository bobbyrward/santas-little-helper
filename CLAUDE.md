# Agent Instructions for Santa's Little Helper

This document provides guidance for AI agents assisting with the development of Santa's Little Helper, a CLI package tracking application.

## Project Overview

Santa's Little Helper is a Python CLI application that helps users track online orders and packages from multiple platforms (shop.app, Etsy, Amazon, and generic orders) across various carriers (FedEx, UPS, USPS, Amazon Logistics).

## Technology Stack

- **Python**: 3.13+
- **Dependency Management**: Poetry
- **CLI Framework**: Typer
- **Database ORM**: SQLAlchemy
- **HTTP Client**: Requests
- **CLI Output**: Rich
- **Testing**: Pytest

## Project Structure

```
santas-little-helper/
├── santas_little_helper/      # Main application package
│   ├── __init__.py            # Package version and metadata
│   ├── main.py                # CLI entry point and commands
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # Database connection and session management
│   ├── commands/              # CLI command modules (future)
│   └── services/              # Business logic and carrier integrations (future)
├── tests/                     # Test files mirroring package structure
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_models.py
│   └── test_database.py
├── .github/
│   └── workflows/             # GitHub Actions workflows
├── pyproject.toml             # Poetry configuration and dependencies
├── README.md                  # User-facing documentation
└── AGENTS.md                  # This file
```

## Best Practices

### Poetry

1. **Dependency Management**:
   - Use `poetry add <package>` for runtime dependencies
   - Use `poetry add --group dev <package>` for development dependencies
   - Keep `pyproject.toml` organized with clear dependency groups

2. **Version Constraints**:
   - Use caret (^) for compatible version updates: `^2.0.0` allows `>=2.0.0 <3.0.0`
   - Pin exact versions only when necessary for stability

3. **Virtual Environment**:
   - Poetry automatically manages virtual environments
   - Run commands with `poetry run <command>`
   - Activate shell with `poetry shell`

4. **Lock File**:
   - Always commit `poetry.lock` to ensure reproducible builds
   - Run `poetry lock --no-update` to refresh lock without updating dependencies

### Typer

1. **Command Structure**:
   - Use `typer.Typer()` to create app instances
   - Decorate functions with `@app.command()` for CLI commands
   - Use type hints for automatic argument parsing and validation

2. **User Experience**:
   - Provide clear help text using docstrings and `help=` parameters
   - Use `typer.Option()` for optional flags with sensible defaults
   - Use `typer.Argument()` for required positional arguments
   - Implement confirmation prompts for destructive operations

3. **Error Handling**:
   - Raise `typer.Exit(code=1)` for error conditions
   - Use `typer.echo()` or Rich console for user feedback
   - Provide helpful error messages with context

### SQLAlchemy

1. **Models**:
   - Use `DeclarativeBase` as base class for all models
   - Use `Mapped[]` type hints with `mapped_column()` for type safety
   - Define relationships with `relationship()` and proper `back_populates`
   - Use enums for fixed-value fields (Platform, Carrier, OrderStatus)

2. **Sessions**:
   - Use context managers or generators for session lifecycle
   - Commit transactions explicitly
   - Handle exceptions and rollback on errors
   - Close sessions properly to avoid connection leaks

3. **Queries**:
   - Use SQLAlchemy 2.0 style queries with `select()`
   - Avoid N+1 queries with `joinedload()` or `selectinload()`
   - Use filters and ordering for efficient data retrieval

4. **Migrations**:
   - For future: Consider Alembic for schema migrations
   - For now: Use `Base.metadata.create_all()` for initial setup

### Requests

1. **HTTP Calls**:
   - Use sessions for connection pooling: `requests.Session()`
   - Set reasonable timeouts: `requests.get(url, timeout=10)`
   - Handle connection errors with try-except blocks

2. **Error Handling**:
   - Check `response.raise_for_status()` for HTTP errors
   - Handle network timeouts and connection errors gracefully
   - Provide user-friendly error messages

3. **Headers and Authentication**:
   - Set User-Agent headers to identify the application
   - Store API keys securely (environment variables, not in code)
   - Respect rate limits with delays between requests

### Rich

1. **Console Output**:
   - Create a `Console()` instance for consistent output
   - Use `console.print()` for formatted text with markup
   - Use `[bold]`, `[green]`, `[red]` for emphasis and status

2. **Tables**:
   - Use `rich.table.Table` for displaying structured data
   - Set appropriate column widths and alignment
   - Use colors to highlight important information

3. **Progress Indicators**:
   - Use `rich.progress.Progress` for long-running operations
   - Show spinners or progress bars for tracking updates
   - Provide meaningful task descriptions

4. **Panels and Layout**:
   - Use `rich.panel.Panel` for grouping related information
   - Use `rich.layout.Layout` for complex multi-section displays

### Pytest

1. **Test Organization**:
   - Mirror package structure in `tests/` directory
   - Name test files as `test_<module>.py`
   - Name test functions as `test_<functionality>()`

2. **Fixtures**:
   - Use `conftest.py` for shared fixtures
   - Create database fixtures with temporary databases
   - Use `pytest.fixture()` with appropriate scopes (function, module, session)

3. **Assertions**:
   - Use clear, specific assertions
   - Test both success and failure cases
   - Use `pytest.raises()` for exception testing

4. **Coverage**:
   - Aim for high test coverage (>80%)
   - Run with `pytest --cov=santas_little_helper --cov-report=html`
   - Focus on critical paths and edge cases

5. **Mocking**:
   - Use `pytest-mock` or `unittest.mock` for external dependencies
   - Mock HTTP calls to avoid network dependency in tests
   - Mock database calls when testing business logic in isolation

## Development Workflow

1. **Adding a New Feature**:
   - Create models in `models.py` if database changes are needed
   - Implement business logic in appropriate service modules
   - Add CLI commands in `main.py` or dedicated command modules
   - Write tests covering new functionality
   - Update README.md with usage examples
   - Run tests: `poetry run pytest`

2. **Adding Dependencies**:
   - Use `poetry add <package>` for runtime dependencies
   - Use `poetry add --group dev <package>` for dev dependencies
   - Update imports and test that code works
   - Commit `poetry.lock` with changes

3. **Database Changes**:
   - Modify models in `models.py`
   - For development, delete the database and reinitialize
   - For production, consider using Alembic migrations

4. **Testing**:
   - Write tests for all new code
   - Run full test suite: `poetry run pytest`
   - Check coverage: `poetry run pytest --cov`
   - Ensure all tests pass before committing

## Common Patterns

### CLI Command Template

```python
@app.command()
def command_name(
    arg: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--flag", "-f", help="Description"),
):
    """Command description for help text."""
    try:
        # Command logic here
        console.print("[green]Success message[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
```

### Database Query Pattern

```python
from santas_little_helper.database import get_session

def get_orders():
    """Retrieve all orders."""
    session_gen = get_session()
    session = next(session_gen)
    try:
        orders = session.query(Order).all()
        return orders
    finally:
        session.close()
```

### HTTP Request Pattern

```python
import requests

def fetch_tracking_info(tracking_number: str, carrier: str):
    """Fetch tracking information from carrier API."""
    try:
        response = requests.get(
            f"https://api.carrier.com/track/{tracking_number}",
            timeout=10,
            headers={"User-Agent": "SantasLittleHelper/0.1.0"},
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        raise Exception("Request timed out")
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch tracking info: {e}")
```

## Code Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Write descriptive docstrings for modules, classes, and functions
- Keep functions focused and single-purpose
- Use meaningful variable and function names
- Format code with Black (consider adding in future)
- Sort imports with isort (consider adding in future)

## Security Considerations

- Never commit API keys or credentials
- Use environment variables for sensitive configuration
- Validate user input before database operations
- Sanitize data before displaying in CLI
- Use parameterized queries (SQLAlchemy handles this)

## Future Enhancements

- Implement carrier API integrations
- Add automatic tracking updates
- Support for notifications (email, desktop)
- Web interface using FastAPI
- Export functionality (CSV, JSON)
- Import from email or web scraping
- Package delivery history and analytics

## Getting Help

When implementing features:
1. Check existing code patterns in the repository
2. Refer to official documentation:
   - [Typer](https://typer.tiangolo.com/)
   - [SQLAlchemy](https://docs.sqlalchemy.org/)
   - [Rich](https://rich.readthedocs.io/)
   - [Pytest](https://docs.pytest.org/)
3. Run tests frequently to catch issues early
4. Ask for clarification when requirements are ambiguous

## Continuous Integration

The project uses GitHub Actions for CI/CD:
- Tests run on every push and pull request
- Uses custom runner: `ohnozombiesrun`
- Ensures code quality and test coverage
