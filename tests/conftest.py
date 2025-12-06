"""Shared pytest fixtures for testing."""

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from santas_little_helper.models import Order, Package, OrderStatus
from santas_little_helper.database import init_db


@pytest.fixture(scope="function")
def test_db_file():
    """Create a temporary database file for testing.

    Function-scoped to ensure each test gets a fresh database file.
    """
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor

    yield path

    # Clean up after test
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def test_session(test_db_file, monkeypatch):
    """Create a database session for testing.

    Function-scoped to ensure each test gets a fresh session and database.
    Sets SANTAS_LITTLE_HELPER_DB environment variable for the test.
    """
    # Set environment variable to use test database
    monkeypatch.setenv("SANTAS_LITTLE_HELPER_DB", test_db_file)

    # Initialize the test database
    init_db()

    # Create session
    engine = create_engine(f"sqlite:///{test_db_file}")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture(scope="function")
def mock_get_session(test_db_file, monkeypatch):
    """Set up test database via environment variable.

    Function-scoped to ensure each test gets its own isolated database.
    """
    # Set environment variable to use test database
    monkeypatch.setenv("SANTAS_LITTLE_HELPER_DB", test_db_file)

    # Initialize the test database
    init_db()

    return test_db_file


@pytest.fixture
def sample_order(test_session) -> Order:
    """Create a sample order without tracking."""
    order = Order(
        platform="etsy",
        order_number="ETSY-123",
        description="Christmas ornament",
        status=OrderStatus.PENDING.value,
    )
    test_session.add(order)
    test_session.commit()
    test_session.refresh(order)
    return order


@pytest.fixture
def sample_order_with_package(test_session) -> Order:
    """Create a sample order with tracking package."""
    order = Order(
        platform="amazon",
        order_number="AMZ-456",
        description="Christmas lights",
        status=OrderStatus.SHIPPED.value,
    )
    test_session.add(order)
    test_session.flush()

    package = Package(
        order_id=order.id,
        tracking_number="1Z999AA10123456784",
        carrier="ups",
        status=OrderStatus.SHIPPED.value,
    )
    test_session.add(package)
    test_session.commit()
    test_session.refresh(order)
    return order


@pytest.fixture
def multiple_orders(test_session) -> list[Order]:
    """Create multiple orders with different statuses."""
    orders = [
        Order(
            platform="etsy",
            description="Pending order",
            status=OrderStatus.PENDING.value,
        ),
        Order(
            platform="amazon",
            description="Shipped order",
            status=OrderStatus.SHIPPED.value,
        ),
        Order(
            platform="shop.app",
            description="Delivered order",
            status=OrderStatus.DELIVERED.value,
        ),
    ]

    for order in orders:
        test_session.add(order)

    test_session.commit()

    for order in orders:
        test_session.refresh(order)

    return orders
