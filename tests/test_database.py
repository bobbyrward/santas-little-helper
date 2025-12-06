"""Tests for database functionality."""

import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from santas_little_helper.models import Base, Order, Package, Platform, Carrier


def test_database_schema_creation():
    """Test that database schema can be created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)

        assert db_path.exists()

        SessionFactory = sessionmaker(bind=engine)
        session = SessionFactory()

        order = Order(
            platform=Platform.ETSY.value,
            order_number="TEST123",
            description="Test order",
        )
        session.add(order)
        session.commit()

        package = Package(
            order_id=order.id,
            tracking_number="TRACK123",
            carrier=Carrier.USPS.value,
        )
        session.add(package)
        session.commit()

        retrieved_order = session.query(Order).first()
        assert retrieved_order is not None
        assert retrieved_order.order_number == "TEST123"
        assert len(retrieved_order.packages) == 1
        assert retrieved_order.packages[0].tracking_number == "TRACK123"

        session.close()
