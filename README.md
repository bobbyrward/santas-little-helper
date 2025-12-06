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

### Initialize Database

First, initialize the database:

```bash
poetry run santas-little-helper init
```

### Adding Orders

Add a new order interactively:

```bash
poetry run santas-little-helper add-order
```

You'll be prompted for:
- Platform (shop.app, etsy, amazon, or generic)
- Order number (optional)
- Description
- Whether tracking is available
- If yes: tracking number and carrier

**Example session:**
```
Platform (shop.app/etsy/amazon/generic): etsy
Order number (optional, press Enter to skip): ETSY-12345
Description: Handmade Christmas ornament
Has tracking number? [y/N]: y
Tracking number: 9400111899562410001234
Carrier (fedex/ups/usps/amazon_logistics): usps
✓ Order added successfully (ID: 1)
  Package tracking: 9400111899562410001234 via usps
```

### Listing Orders

View all orders in a formatted table:

```bash
poetry run santas-little-helper list
```

Filter orders by various criteria:

```bash
# Show only active orders (not delivered or cancelled)
poetry run santas-little-helper list --active

# Show only delivered orders
poetry run santas-little-helper list --delivered

# Filter by status
poetry run santas-little-helper list --status in_transit

# Filter by platform
poetry run santas-little-helper list --platform etsy

# Show only orders with tracking
poetry run santas-little-helper list --has-tracking

# Show only orders without tracking
poetry run santas-little-helper list --no-tracking

# Combine filters
poetry run santas-little-helper list --platform etsy --active
```

### Viewing Order Details

Show detailed information for a specific order:

```bash
poetry run santas-little-helper show 1
```

### Adding Tracking

Add tracking information to an existing order:

```bash
poetry run santas-little-helper add-tracking 1
```

You'll be prompted for the tracking number and carrier.

### Updating Status

Manually update order or package status:

```bash
poetry run santas-little-helper update-status 1
```

You'll be prompted for:
- Whether to update the order or a specific package
- The new status
- Additional information based on status:
  - **DELIVERED**: Delivery timestamp (defaults to now)
  - **IN_TRANSIT** or **OUT_FOR_DELIVERY**: Optional location

**Available statuses:**
- `pending` - Order placed, not shipped
- `shipped` - Package has shipped
- `in_transit` - Package is in transit
- `out_for_delivery` - Package is out for delivery
- `delivered` - Package has been delivered
- `exception` - Delivery exception occurred
- `cancelled` - Order was cancelled

### Version

Show the version:

```bash
poetry run santas-little-helper version
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
