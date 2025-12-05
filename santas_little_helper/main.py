"""Main CLI entry point."""

import typer
from rich.console import Console

from santas_little_helper.models import Order, Package, Platform, Carrier, OrderStatus
from santas_little_helper.database import get_session

app = typer.Typer(
    help="Santa's Little Helper - Track your packages in one place",
    no_args_is_help=True
)
console = Console()


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
    platform_input = typer.prompt(
        "Platform (shop.app/etsy/amazon/generic)"
    ).lower()

    # Validate against Platform enum
    try:
        platform = Platform(platform_input)
    except ValueError:
        console.print(f"[red]✗ Invalid platform: {platform_input}[/red]")
        console.print(f"[yellow]Must be one of: {', '.join([p.value for p in Platform])}[/yellow]")
        raise typer.Exit(code=1)

    # Prompt for order number (optional)
    order_number = typer.prompt(
        "Order number (optional, press Enter to skip)",
        default="",
        show_default=False
    ) or None

    # Prompt for description
    description = typer.prompt("Description")

    # Ask if tracking is available
    has_tracking = typer.confirm("Has tracking number?", default=False)

    tracking_number = None
    carrier = None

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
            console.print(f"[yellow]Must be one of: {', '.join([c.value for c in Carrier])}[/yellow]")
            raise typer.Exit(code=1)

    # Create Order in database
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Create the order
        order = Order(
            platform=platform.value,
            order_number=order_number,
            description=description,
            status=OrderStatus.PENDING.value if not has_tracking else OrderStatus.SHIPPED.value
        )
        session.add(order)
        session.flush()  # Get the order ID

        # If tracking provided, create Package
        if has_tracking:
            package = Package(
                order_id=order.id,
                tracking_number=tracking_number,
                carrier=carrier.value,
                status=OrderStatus.SHIPPED.value
            )
            session.add(package)

        session.commit()

        # Success message
        console.print(f"[green]✓ Order added successfully (ID: {order.id})[/green]")
        if has_tracking:
            console.print(f"[green]  Package tracking: {tracking_number} via {carrier.value}[/green]")

    except Exception as e:
        session.rollback()
        console.print(f"[red]✗ Database error: {e}[/red]")
        raise typer.Exit(code=1)

    finally:
        session.close()


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
