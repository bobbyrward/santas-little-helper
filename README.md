# Santa's Little Helper 🎅📦

A CLI tool to track online orders and packages from multiple platforms in one place.

## Features

- Track orders from multiple platforms:
  - shop.app
  - Etsy
  - Amazon
  - Generic orders (tracking number only)

- Monitor packages across carriers:
  - FedEx
  - UPS
  - USPS
  - Amazon Logistics

- Local SQLite database for state management
- Rich CLI interface with formatted output

## Installation

### Prerequisites

- Python 3.13+
- Poetry

### Setup

```bash
# Install dependencies
poetry install

# Initialize the database
poetry run python -c "from santas_little_helper.database import init_db; init_db()"
```

## Usage

```bash
# Show version
poetry run santas-little-helper version

# More commands coming soon...
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Running Tests with Coverage

```bash
poetry run pytest --cov=santas_little_helper --cov-report=html
```

## Project Structure

```
santas-little-helper/
├── santas_little_helper/
│   ├── __init__.py       # Package metadata
│   ├── main.py           # CLI entry point
│   ├── models.py         # Database models
│   └── database.py       # Database setup
├── tests/                # Test files
├── pyproject.toml        # Poetry configuration
└── README.md             # This file
```

## License

MIT
