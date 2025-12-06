"""Utility functions for CLI commands."""

from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from santas_little_helper.models import Order, Platform, Carrier, OrderStatus

console = Console()

# Status color mapping
STATUS_COLORS = {
    OrderStatus.DELIVERED.value: "green",
    OrderStatus.OUT_FOR_DELIVERY.value: "bright_green",
    OrderStatus.IN_TRANSIT.value: "yellow",
    OrderStatus.SHIPPED.value: "yellow",
    OrderStatus.PENDING.value: "cyan",
    OrderStatus.EXCEPTION.value: "red",
    OrderStatus.CANCELLED.value: "dim",
}

# Status display order (most urgent first)
STATUS_ORDER = [
    OrderStatus.OUT_FOR_DELIVERY.value,
    OrderStatus.IN_TRANSIT.value,
    OrderStatus.SHIPPED.value,
    OrderStatus.PENDING.value,
    OrderStatus.DELIVERED.value,
    OrderStatus.EXCEPTION.value,
    OrderStatus.CANCELLED.value,
]


def parse_platform(value: str) -> Platform:
    """Parse platform string to enum, case-insensitive.

    Args:
        value: Platform string to parse

    Returns:
        Platform enum value

    Raises:
        ValueError: If platform is invalid
    """
    try:
        return Platform(value.lower())
    except ValueError:
        valid_platforms = ", ".join([p.value for p in Platform])
        raise ValueError(f"Invalid platform: {value}. Valid options: {valid_platforms}")


def parse_carrier(value: str) -> Carrier:
    """Parse carrier string to enum, case-insensitive.

    Args:
        value: Carrier string to parse

    Returns:
        Carrier enum value

    Raises:
        ValueError: If carrier is invalid
    """
    try:
        return Carrier(value.lower())
    except ValueError:
        valid_carriers = ", ".join([c.value for c in Carrier])
        raise ValueError(f"Invalid carrier: {value}. Valid options: {valid_carriers}")


def parse_status(value: str) -> OrderStatus:
    """Parse status string to enum, case-insensitive.

    Args:
        value: Status string to parse

    Returns:
        OrderStatus enum value

    Raises:
        ValueError: If status is invalid
    """
    try:
        return OrderStatus(value.lower())
    except ValueError:
        valid_statuses = ", ".join([s.value for s in OrderStatus])
        raise ValueError(f"Invalid status: {value}. Valid options: {valid_statuses}")


def format_status(status_value: str) -> str:
    """Format status with color coding.

    Args:
        status_value: Status string to format

    Returns:
        Rich-formatted status string with color
    """
    color = STATUS_COLORS.get(status_value, "white")
    return f"[{color}]{status_value}[/{color}]"


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format, or None

    Returns:
        Formatted datetime string, or "—" if None
    """
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M")
    return "—"


def display_order_details(order: Order) -> None:
    """Display detailed order information in Rich panels.

    Args:
        order: Order object to display
    """
    # Display order information panel
    order_info = f"""[bold]Order #{order.id}[/bold]

Platform:     {order.platform}
Order Number: {order.order_number or '—'}
Description:  {order.description or '—'}
Status:       {format_status(order.status)}
Created:      {format_datetime(order.created_at)}
Updated:      {format_datetime(order.updated_at)}
"""
    console.print(Panel(order_info, title="Order Information", border_style="blue"))

    # Display package tracking information
    if order.packages:
        for package in order.packages:
            package_info = f"""[bold]Package #{package.id}[/bold]

Tracking:         {package.tracking_number}
Carrier:          {package.carrier}
Status:           {format_status(package.status)}
Last Location:    {package.last_location or 'Unknown'}
Est. Delivery:    {package.estimated_delivery.strftime('%Y-%m-%d') if package.estimated_delivery else 'Unknown'}
Delivered At:     {format_datetime(package.delivered_at)}
"""
            console.print(
                Panel(package_info, title="Package Tracking", border_style="green")
            )
    else:
        no_tracking_info = "[yellow]No tracking information available[/yellow]"
        console.print(
            Panel(
                no_tracking_info,
                title="Package Tracking",
                border_style="yellow",
            )
        )
