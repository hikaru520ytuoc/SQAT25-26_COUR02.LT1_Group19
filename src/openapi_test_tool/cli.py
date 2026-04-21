from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from openapi_test_tool.config import AppConfig

app = typer.Typer(
    add_completion=False,
    help="CLI skeleton for generating and executing functional API tests from OpenAPI specs.",
)
console = Console()


@app.command()
def main(
    spec: Path = typer.Option(..., "--spec", help="Path to OpenAPI spec file (.yaml, .yml, .json)."),
    base_url: str = typer.Option(..., "--base-url", help="Base URL of the target REST API."),
    output: Path = typer.Option(Path("reports"), "--output", help="Directory to store generated reports."),
) -> None:
    """Run the initial project skeleton."""
    console.print(Panel.fit("OpenAPI Test Tool - Skeleton CLI", style="bold cyan"))

    if not spec.exists():
        console.print(f"[bold red]Error:[/bold red] Spec file does not exist: {spec}")
        raise typer.Exit(code=1)

    output.mkdir(parents=True, exist_ok=True)

    config = AppConfig(
        spec=spec.resolve(),
        base_url=base_url,
        output=output.resolve(),
    )

    table = Table(title="Input Summary", show_header=False)
    table.add_column("Field", style="bold green")
    table.add_column("Value", style="white")
    table.add_row("Spec file", str(config.spec))
    table.add_row("Base URL", config.base_url)
    table.add_row("Output directory", str(config.output))

    console.print(table)
    console.print("[bold green]Skeleton check completed successfully.[/bold green]")
    console.print(
        "[yellow]Current status:[/yellow] Project structure, CLI, Docker, and test scaffolding are ready. "
        "Business logic will be implemented in later milestones."
    )


if __name__ == "__main__":
    app()
