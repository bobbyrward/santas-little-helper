"""Tests for database models."""

from santas_little_helper.models import (
    Order,
    Package,
    Platform,
    Carrier,
    OrderStatus,
)


def test_order_creation():
    """Test creating an Order instance."""
    order = Order(
        platform=Platform.AMAZON.value,
        order_number="123-4567890-1234567",
        description="Test order",
        status=OrderStatus.PENDING.value,
    )
    assert order.platform == Platform.AMAZON.value
    assert order.order_number == "123-4567890-1234567"
    assert order.status == OrderStatus.PENDING.value


def test_package_creation():
    """Test creating a Package instance."""
    package = Package(
        order_id=1,
        tracking_number="1Z999AA10123456784",
        carrier=Carrier.UPS.value,
        status=OrderStatus.IN_TRANSIT.value,
    )
    assert package.tracking_number == "1Z999AA10123456784"
    assert package.carrier == Carrier.UPS.value
    assert package.status == OrderStatus.IN_TRANSIT.value


def test_platform_enum():
    """Test Platform enum values."""
    assert Platform.SHOP_APP.value == "shop.app"
    assert Platform.ETSY.value == "etsy"
    assert Platform.AMAZON.value == "amazon"
    assert Platform.GENERIC.value == "generic"


def test_carrier_enum():
    """Test Carrier enum values."""
    assert Carrier.FEDEX.value == "fedex"
    assert Carrier.UPS.value == "ups"
    assert Carrier.USPS.value == "usps"
    assert Carrier.AMAZON_LOGISTICS.value == "amazon_logistics"
    assert Carrier.ONTRAC.value == "ontrac"


def test_order_status_enum():
    """Test OrderStatus enum values."""
    assert OrderStatus.PENDING.value == "pending"
    assert OrderStatus.SHIPPED.value == "shipped"
    assert OrderStatus.IN_TRANSIT.value == "in_transit"
    assert OrderStatus.OUT_FOR_DELIVERY.value == "out_for_delivery"
    assert OrderStatus.DELIVERED.value == "delivered"
    assert OrderStatus.EXCEPTION.value == "exception"
    assert OrderStatus.CANCELLED.value == "cancelled"
