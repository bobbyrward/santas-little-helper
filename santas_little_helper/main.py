"""Main CLI entry point."""

import typer
from rich.console import Console

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


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
