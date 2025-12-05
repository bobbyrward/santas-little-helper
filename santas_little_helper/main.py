"""Main CLI entry point."""

from datetime import datetime
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from santas_little_helper.models import Order, Package, Platform, Carrier, OrderStatus
from santas_little_helper.database import get_session

app = typer.Typer(
    help="Santa's Little Helper - Track your packages in one place",
    no_args_is_help=True,
)
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


@app.command()
def version():
    """Show version information."""
    from santas_little_helper import __version__

    console.print(f"Santa's Little Helper v{__version__}")


@app.command()
def init():
    """Initialize the database."""
    from santas_little_helper.database import init_db

    try:
        init_db()
        console.print("[green]Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="add-order")
def add_order():
    """Add a new order interactively."""
    # Prompt for platform with validation
    platform_input = typer.prompt("Platform (shop.app/etsy/amazon/generic)").lower()

    # Validate against Platform enum
    try:
        platform = Platform(platform_input)
    except ValueError:
        console.print(f"[red]✗ Invalid platform: {platform_input}[/red]")
        console.print(
            f"[yellow]Must be one of: {', '.join([p.value for p in Platform])}[/yellow]"
        )
        raise typer.Exit(code=1)

    # Prompt for order number (optional)
    order_number = (
        typer.prompt(
            "Order number (optional, press Enter to skip)",
            default="",
            show_default=False,
        )
        or None
    )

    # Prompt for description
    description = typer.prompt("Description")

    # Ask if tracking is available
    has_tracking = typer.confirm("Has tracking number?", default=False)

    tracking_number = None
    carrier = None
    carrier_name = ""

    if has_tracking:
        tracking_number = typer.prompt("Tracking number")
        carrier_input = typer.prompt(
            "Carrier (fedex/ups/usps/amazon_logistics)"
        ).lower()

        # Validate carrier against Carrier enum
        try:
            carrier = Carrier(carrier_input)
        except ValueError:
            console.print(f"[red]✗ Invalid carrier: {carrier_input}[/red]")
            console.print(
                f"[yellow]Must be one of: {', '.join([c.value for c in Carrier])}[/yellow]"
            )
            raise typer.Exit(code=1)

    if carrier:
        carrier_name = carrier.value

    with get_session() as session:
        try:
            # Create the order
            order = Order(
                platform=platform.value,
                order_number=order_number,
                description=description,
                status=OrderStatus.PENDING.value
                if not has_tracking
                else OrderStatus.SHIPPED.value,
            )
            session.add(order)
            session.flush()  # Get the order ID

            # If tracking provided, create Package
            if has_tracking:
                package = Package(
                    order_id=order.id,
                    tracking_number=tracking_number,
                    carrier=carrier_name,
                    status=OrderStatus.SHIPPED.value,
                )
                session.add(package)

            session.commit()

            # Success message
            console.print(f"[green]✓ Order added successfully (ID: {order.id})[/green]")
            if has_tracking:
                console.print(
                    f"[green]  Package tracking: {tracking_number} via {carrier_name}[/green]"
                )

        except IntegrityError as e:
            session.rollback()
            if "tracking_number" in str(e):
                console.print("[red]✗ Tracking number already exists in database[/red]")
            else:
                console.print(f"[red]✗ Database constraint error: {e}[/red]")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[red]✗ Database error: {e}[/red]")
            raise typer.Exit(code=1)


@app.command(name="list")
def list_orders(
    status: str = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status (pending/shipped/in_transit/delivered/etc.)",
    ),
    platform: str = typer.Option(
        None,
        "--platform",
        "-p",
        help="Filter by platform (shop.app/etsy/amazon/generic)",
    ),
    has_tracking: bool = typer.Option(
        None, "--has-tracking", help="Show only orders with tracking"
    ),
    no_tracking: bool = typer.Option(
        None, "--no-tracking", help="Show only orders without tracking"
    ),
    delivered: bool = typer.Option(
        False, "--delivered", help="Show only delivered orders"
    ),
    active: bool = typer.Option(
        False, "--active", help="Show only active (non-delivered, non-cancelled) orders"
    ),
):
    """List all orders in a formatted table.

    Examples:
      santas-little-helper list --active
      santas-little-helper list --platform etsy
      santas-little-helper list --status in_transit
      santas-little-helper list --no-tracking
    """
    with get_session() as session:
        try:
            # Build query with filters
            query = session.query(Order).options(joinedload(Order.packages))

            # Validate and apply status filter
            if status:
                status_lower = status.lower()
                try:
                    status_enum = OrderStatus(status_lower)
                    query = query.filter(Order.status == status_enum.value)
                except ValueError:
                    console.print(f"[red]✗ Invalid status: {status}[/red]")
                    console.print(
                        f"[yellow]Must be one of: {', '.join([s.value for s in OrderStatus])}[/yellow]"
                    )
                    raise typer.Exit(code=1)

            # Validate and apply platform filter
            if platform:
                platform_lower = platform.lower()
                try:
                    platform_enum = Platform(platform_lower)
                    query = query.filter(Order.platform == platform_enum.value)
                except ValueError:
                    console.print(f"[red]✗ Invalid platform: {platform}[/red]")
                    console.print(
                        f"[yellow]Must be one of: {', '.join([p.value for p in Platform])}[/yellow]"
                    )
                    raise typer.Exit(code=1)

            # Apply tracking filters
            if has_tracking:
                query = query.filter(Order.packages.any())
            elif no_tracking:
                query = query.filter(~Order.packages.any())

            # Apply convenience filters
            if delivered:
                query = query.filter(Order.status == OrderStatus.DELIVERED.value)

            if active:
                query = query.filter(
                    Order.status.notin_(
                        [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value]
                    )
                )

            # Execute query
            orders = query.all()

            # Build filter description for title and empty message
            filters = []
            if status:
                filters.append(f"Status: {status}")
            if platform:
                filters.append(f"Platform: {platform}")
            if has_tracking:
                filters.append("With Tracking")
            if no_tracking:
                filters.append("No Tracking")
            if delivered:
                filters.append("Delivered Only")
            if active:
                filters.append("Active Only")

            # Empty state
            if not orders:
                if filters:
                    console.print(
                        "[yellow]No orders match the specified filters.[/yellow]"
                    )
                    console.print(
                        "[dim]Try different filters or use 'list' without options to see all orders.[/dim]"
                    )
                else:
                    console.print(
                        "[yellow]No orders found. Add one with 'santas-little-helper add-order'[/yellow]"
                    )
                return

            # Group orders by status
            grouped = {}
            for order in orders:
                status = order.status
                if status not in grouped:
                    grouped[status] = []
                grouped[status].append(order)

            # Sort within each group by estimated_delivery, then description
            for status in grouped:
                grouped[status].sort(
                    key=lambda o: (
                        # Get earliest estimated delivery from packages, or max date if none
                        min(
                            (
                                p.estimated_delivery
                                for p in o.packages
                                if p.estimated_delivery
                            ),
                            default=datetime.max,
                        ),
                        o.description or "",
                    )
                )

            # Create Rich table with filter-aware title
            title = "Christmas Orders"
            if filters:
                title = f"Christmas Orders ({', '.join(filters)})"
            table = Table(title=title, show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim", width=6)
            table.add_column("Platform", width=12)
            table.add_column("Description", width=30)
            table.add_column("Tracking #", width=20)
            table.add_column("Carrier", width=15)
            table.add_column("Status", width=15)
            table.add_column("Est. Delivery", width=12)

            # Add rows grouped by status
            for status in STATUS_ORDER:
                if status not in grouped:
                    continue

                for order in grouped[status]:
                    color = STATUS_COLORS.get(order.status, "white")

                    # Get tracking info from first package or show "No tracking"
                    if order.packages:
                        pkg = order.packages[0]
                        tracking = pkg.tracking_number
                        carrier = pkg.carrier
                        est_delivery = (
                            pkg.estimated_delivery.strftime("%Y-%m-%d")
                            if pkg.estimated_delivery
                            else "—"
                        )
                    else:
                        tracking = "[dim]No tracking[/dim]"
                        carrier = "—"
                        est_delivery = "—"

                    table.add_row(
                        str(order.id),
                        order.platform,
                        order.description or "—",
                        tracking,
                        carrier,
                        f"[{color}]{order.status}[/{color}]",
                        est_delivery,
                    )

            console.print(table)

            # Print summary footer
            total = len(orders)
            status_counts = {}
            for status in STATUS_ORDER:
                count = len(grouped.get(status, []))
                if count > 0:
                    status_counts[status] = count

            # Build summary line
            summary_parts = []
            if status_counts.get(OrderStatus.DELIVERED.value):
                summary_parts.append(
                    f"Delivered: {status_counts[OrderStatus.DELIVERED.value]}"
                )
            if status_counts.get(OrderStatus.IN_TRANSIT.value):
                summary_parts.append(
                    f"In Transit: {status_counts[OrderStatus.IN_TRANSIT.value]}"
                )
            if status_counts.get(OrderStatus.SHIPPED.value):
                summary_parts.append(
                    f"Shipped: {status_counts[OrderStatus.SHIPPED.value]}"
                )
            if status_counts.get(OrderStatus.PENDING.value):
                summary_parts.append(
                    f"Pending: {status_counts[OrderStatus.PENDING.value]}"
                )

            console.print(f"\nTotal orders: {total}")
            if summary_parts:
                console.print(f"{' | '.join(summary_parts)}")

        except Exception as e:
            console.print(f"[red]✗ Database error: {e}[/red]")
            raise typer.Exit(code=1)


def format_status(status_value: str) -> str:
    """Format status with color coding."""
    color = STATUS_COLORS.get(status_value, "white")
    return f"[{color}]{status_value}[/{color}]"


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M")
    return "—"


@app.command(name="show")
def show_order(
    order_id: int = typer.Argument(..., help="Order ID to display"),
):
    """Show detailed information for a specific order."""
    with get_session() as session:
        try:
            # Query order with eager loading of packages
            order = (
                session.query(Order)
                .options(joinedload(Order.packages))
                .filter(Order.id == order_id)
                .first()
            )

            if not order:
                console.print(f"[red]✗ Order {order_id} not found[/red]")
                raise typer.Exit(code=1)

            # Display order information panel
            order_info = f"""[bold]Order #{order.id}[/bold]

Platform:     {order.platform}
Order Number: {order.order_number or '—'}
Description:  {order.description or '—'}
Status:       {format_status(order.status)}
Created:      {format_datetime(order.created_at)}
Updated:      {format_datetime(order.updated_at)}
"""
            console.print(
                Panel(order_info, title="Order Information", border_style="blue")
            )

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
                        Panel(
                            package_info, title="Package Tracking", border_style="green"
                        )
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

        except Exception as e:
            console.print(f"[red]✗ Database error: {e}[/red]")
            raise typer.Exit(code=1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
