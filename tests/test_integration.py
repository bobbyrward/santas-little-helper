"""Integration tests for full CLI workflows."""

from typer.testing import CliRunner

from santas_little_helper.main import app
from santas_little_helper.models import OrderStatus

runner = CliRunner()


def test_full_workflow(mock_get_session):
    """Test complete user workflow from adding order to delivery."""
    # 1. Add order without tracking
    result = runner.invoke(
        app, ["add-order"], input="etsy\n\nChristmas sweater\nn\n"
    )
    assert result.exit_code == 0
    assert "Order added successfully" in result.stdout

    # Extract order ID from output
    import re
    match = re.search(r"ID: (\d+)", result.stdout)
    assert match is not None
    order_id = match.group(1)

    # 2. List orders - should show pending
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Christmas sweater" in result.stdout
    assert "pending" in result.stdout.lower()

    # 3. Add tracking to order
    result = runner.invoke(app, ["add-tracking", order_id], input="1Z999\nups\n")
    assert result.exit_code == 0
    assert "Tracking added" in result.stdout
    assert "1Z999" in result.stdout

    # 4. Show order details
    result = runner.invoke(app, ["show", order_id])
    assert result.exit_code == 0
    assert "1Z999" in result.stdout
    assert "ups" in result.stdout

    # 5. Update status to in_transit with location
    result = runner.invoke(
        app, ["update-status", order_id], input="order\nin_transit\nMemphis, TN\n"
    )
    assert result.exit_code == 0
    assert "Status updated to in_transit" in result.stdout

    # 6. Update status to delivered
    result = runner.invoke(
        app, ["update-status", order_id], input="order\ndelivered\ny\n"
    )
    assert result.exit_code == 0
    assert "Status updated to delivered" in result.stdout

    # 7. List delivered orders
    result = runner.invoke(app, ["list", "--delivered"])
    assert result.exit_code == 0
    assert "Christmas sweater" in result.stdout


def test_multiple_orders_filtering(mock_get_session, multiple_orders):
    """Test listing and filtering multiple orders."""
    # List all orders
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Pending order" in result.stdout
    assert "Shipped order" in result.stdout
    assert "Delivered order" in result.stdout

    # Filter by status - pending
    result = runner.invoke(app, ["list", "--status", "pending"])
    assert result.exit_code == 0
    assert "Pending order" in result.stdout
    assert "Shipped order" not in result.stdout

    # Filter by status - delivered
    result = runner.invoke(app, ["list", "--delivered"])
    assert result.exit_code == 0
    assert "Delivered order" in result.stdout
    assert "Pending order" not in result.stdout

    # Filter by platform
    result = runner.invoke(app, ["list", "--platform", "etsy"])
    assert result.exit_code == 0
    assert "Pending order" in result.stdout
    assert "Shipped order" not in result.stdout

    # Filter active orders
    result = runner.invoke(app, ["list", "--active"])
    assert result.exit_code == 0
    assert "Pending order" in result.stdout
    assert "Shipped order" in result.stdout
    assert "Delivered order" not in result.stdout


def test_add_order_with_tracking(mock_get_session):
    """Test adding order with tracking information."""
    result = runner.invoke(
        app,
        ["add-order"],
        input="amazon\nAMZ-123\nChristmas tree\ny\n1Z999AA10123456784\nups\n",
    )
    assert result.exit_code == 0
    assert "Order added successfully" in result.stdout
    assert "1Z999AA10123456784" in result.stdout
    assert "ups" in result.stdout


def test_error_handling_invalid_platform(mock_get_session):
    """Test error handling for invalid platform."""
    result = runner.invoke(app, ["add-order"], input="invalid_platform\n")
    assert result.exit_code == 1
    assert "Invalid platform" in result.stdout


def test_error_handling_invalid_carrier(mock_get_session):
    """Test error handling for invalid carrier."""
    result = runner.invoke(
        app, ["add-order"], input="etsy\n\nTest item\ny\n123456\ninvalid_carrier\n"
    )
    assert result.exit_code == 1
    assert "Invalid carrier" in result.stdout


def test_error_handling_invalid_status_filter(mock_get_session):
    """Test error handling for invalid status filter."""
    result = runner.invoke(app, ["list", "--status", "invalid_status"])
    assert result.exit_code == 1
    assert "Invalid status" in result.stdout


def test_error_handling_nonexistent_order(mock_get_session):
    """Test error handling for non-existent order."""
    result = runner.invoke(app, ["show", "999"])
    assert result.exit_code == 1
    assert "Order 999 not found" in result.stdout


def test_update_status_invalid_status(mock_get_session, sample_order):
    """Test updating status with invalid status value."""
    result = runner.invoke(
        app, ["update-status", str(sample_order.id)], input="order\ninvalid_status\n"
    )
    assert result.exit_code == 1
    assert "Invalid status" in result.stdout


def test_tracking_uniqueness_constraint(mock_get_session, sample_order_with_package):
    """Test that duplicate tracking numbers are rejected."""
    # Try to add another order with same tracking number
    result = runner.invoke(
        app,
        ["add-order"],
        input="etsy\n\nTest item\ny\n1Z999AA10123456784\nfedex\n",
    )
    assert result.exit_code == 1
    assert "Tracking number already exists" in result.stdout


def test_list_no_orders(mock_get_session):
    """Test listing when no orders exist."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No orders found" in result.stdout or "Total orders: 0" in result.stdout


def test_list_with_no_tracking_filter(mock_get_session, sample_order):
    """Test filtering orders without tracking."""
    result = runner.invoke(app, ["list", "--no-tracking"])
    assert result.exit_code == 0
    assert "Christmas ornament" in result.stdout


def test_list_with_has_tracking_filter(
    mock_get_session, sample_order, sample_order_with_package
):
    """Test filtering orders with tracking."""
    result = runner.invoke(app, ["list", "--has-tracking"])
    assert result.exit_code == 0
    assert "Christmas lights" in result.stdout
    assert "Christmas ornament" not in result.stdout


def test_add_tracking_to_order_with_tracking(mock_get_session, sample_order_with_package):
    """Test adding additional tracking to order that already has tracking."""
    result = runner.invoke(
        app,
        ["add-tracking", str(sample_order_with_package.id)],
        input="y\nNEWTRACK123\nfedex\n",
    )
    assert result.exit_code == 0
    assert "Tracking added" in result.stdout


def test_package_status_update(mock_get_session, sample_order_with_package):
    """Test updating individual package status."""
    result = runner.invoke(
        app,
        ["update-status", str(sample_order_with_package.id)],
        input="package\nout_for_delivery\n\n",
    )
    assert result.exit_code == 0
    assert "Status updated to out_for_delivery" in result.stdout
