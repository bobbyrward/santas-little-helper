"""Database models for tracking orders and packages."""

from datetime import datetime, UTC
from enum import Enum
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Platform(str, Enum):
    """Supported order platforms."""
    SHOP_APP = "shop.app"
    ETSY = "etsy"
    AMAZON = "amazon"
    GENERIC = "generic"


class Carrier(str, Enum):
    """Supported shipping carriers."""
    FEDEX = "fedex"
    UPS = "ups"
    USPS = "usps"
    AMAZON_LOGISTICS = "amazon_logistics"


class OrderStatus(str, Enum):
    """Order status values."""
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
    CANCELLED = "cancelled"


def utc_now():
    """Return current UTC time."""
    return datetime.now(UTC)


class Order(Base):
    """Order tracking model."""
    
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(50))
    order_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    order_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=OrderStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )
    
    packages: Mapped[list["Package"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class Package(Base):
    """Package tracking model."""
    
    __tablename__ = "packages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    tracking_number: Mapped[str] = mapped_column(String(100), unique=True)
    carrier: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default=OrderStatus.PENDING.value)
    last_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    estimated_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )
    
    order: Mapped["Order"] = relationship(back_populates="packages")
