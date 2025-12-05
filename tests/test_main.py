"""Tests for main CLI."""

from typer.testing import CliRunner

from santas_little_helper.main import app
from santas_little_helper import __version__

runner = CliRunner()


def test_version_command():
    """Test version command output."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
