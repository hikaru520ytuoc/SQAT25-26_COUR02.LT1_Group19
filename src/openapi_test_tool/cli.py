from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from openapi_test_tool.config import AppConfig
from openapi_test_tool.parser import OpenAPILoaderError, SchemaResolverError, extract_spec_summary, load_openapi_spec

app = typer.Typer(
    add_completion=False,
    help="CLI tool for generating and executing functional API tests from OpenAPI specs.",
)
console = Console()


@app.command()
def main(
    spec: Path = typer.Option(..., "--spec", help="Path to OpenAPI spec file (.yaml, .yml, .json)."),
    base_url: str = typer.Option(..., "--base-url", help="Base URL of the target REST API."),
    output: Path = typer.Option(Path("reports"), "--output", help="Directory to store generated reports."),
) -> None:
    """Load and parse an OpenAPI spec, then print a small summary."""
    console.print(Panel.fit("OpenAPI Test Tool - Parser Stage", style="bold cyan"))

    output.mkdir(parents=True, exist_ok=True)

    try:
        config = AppConfig(spec=spec.resolve(), base_url=base_url, output=output.resolve())
        spec_document = load_openapi_spec(config.spec)
        summary = extract_spec_summary(spec_document)
    except (OpenAPILoaderError, SchemaResolverError, ValueError) as exc:
        console.print(f"[bold red]Parse error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    input_table = Table(title="Input Summary", show_header=False)
    input_table.add_column("Field", style="bold green")
    input_table.add_column("Value", style="white")
    input_table.add_row("Spec file", str(config.spec))
    input_table.add_row("Base URL", config.base_url)
    input_table.add_row("Output directory", str(config.output))
    console.print(input_table)

    summary_table = Table(title="OpenAPI Summary")
    summary_table.add_column("Metric", style="bold magenta")
    summary_table.add_column("Value", style="white")
    summary_table.add_row("OpenAPI version", summary.openapi_version)
    summary_table.add_row("Title", summary.title or "-")
    summary_table.add_row("Spec version", summary.version or "-")
    summary_table.add_row("Path count", str(summary.path_count))
    summary_table.add_row("Operation count", str(summary.operation_count))
    console.print(summary_table)

    endpoints_table = Table(title="Endpoints")
    endpoints_table.add_column("Method", style="bold cyan")
    endpoints_table.add_column("Path", style="white")
    endpoints_table.add_column("Operation ID", style="green")
    endpoints_table.add_column("Summary", style="yellow")

    for endpoint in summary.endpoints:
        endpoints_table.add_row(
            endpoint.method,
            endpoint.path,
            endpoint.operation_id or "-",
            endpoint.summary or "-",
        )

    console.print(endpoints_table)
    console.print("[bold green]OpenAPI parsing completed successfully.[/bold green]")


if __name__ == "__main__":
    app()
