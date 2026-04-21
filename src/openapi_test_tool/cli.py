from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from openapi_test_tool.config import AppConfig
from openapi_test_tool.generator import generate_test_suite
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
    """Load an OpenAPI spec, parse it, and generate preview test cases."""
    console.print(Panel.fit("OpenAPI Test Tool - Generator Stage", style="bold cyan"))

    output.mkdir(parents=True, exist_ok=True)

    try:
        config = AppConfig(spec=spec.resolve(), base_url=base_url, output=output.resolve())
        spec_document = load_openapi_spec(config.spec)
        spec_summary = extract_spec_summary(spec_document)
        test_suite = generate_test_suite(spec_summary)
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
    summary_table.add_row("OpenAPI version", spec_summary.openapi_version)
    summary_table.add_row("Title", spec_summary.title or "-")
    summary_table.add_row("Spec version", spec_summary.version or "-")
    summary_table.add_row("Path count", str(spec_summary.path_count))
    summary_table.add_row("Operation count", str(spec_summary.operation_count))
    console.print(summary_table)

    endpoints_table = Table(title="Endpoints")
    endpoints_table.add_column("Method", style="bold cyan")
    endpoints_table.add_column("Path", style="white")
    endpoints_table.add_column("Operation ID", style="green")
    endpoints_table.add_column("Summary", style="yellow")

    for endpoint in spec_summary.endpoints:
        endpoints_table.add_row(
            endpoint.method,
            endpoint.path,
            endpoint.operation_id or "-",
            endpoint.summary or "-",
        )

    console.print(endpoints_table)
    console.print("[bold green]OpenAPI parsing completed successfully.[/bold green]")

    test_suite_table = Table(title="Generated Test Case Summary")
    test_suite_table.add_column("Metric", style="bold magenta")
    test_suite_table.add_column("Value", style="white")
    test_suite_table.add_row("Total test cases", str(test_suite.total_count))
    test_suite_table.add_row("Valid cases", str(test_suite.valid_count))
    test_suite_table.add_row("Invalid cases", str(test_suite.invalid_count))
    console.print(test_suite_table)

    preview_table = Table(title="Test Case Preview (first 5)")
    preview_table.add_column("ID", style="bold cyan")
    preview_table.add_column("Category", style="green")
    preview_table.add_column("Type", style="yellow")
    preview_table.add_column("Method", style="white")
    preview_table.add_column("Path", style="white")
    preview_table.add_column("Name", style="white")

    for test_case in test_suite.test_cases[:5]:
        preview_table.add_row(
            test_case.test_id,
            test_case.category.value,
            test_case.test_type.value,
            test_case.method,
            test_case.endpoint_path,
            test_case.name,
        )

    console.print(preview_table)
    console.print("[bold green]Test case generation completed successfully.[/bold green]")


if __name__ == "__main__":
    app()
