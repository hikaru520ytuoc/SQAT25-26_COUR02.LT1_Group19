from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from openapi_test_tool.config import AppConfig
from openapi_test_tool.executor import execute_test_suite
from openapi_test_tool.generator import generate_test_suite
from openapi_test_tool.parser import OpenAPILoaderError, SchemaResolverError, extract_spec_summary, load_openapi_spec
from openapi_test_tool.reporter import build_report_context, write_report_files

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
    """Load a spec, generate test cases, execute them, write reports, and print a summary."""
    console.print(Panel.fit("OpenAPI Test Tool - Reporter Stage", style="bold cyan"))

    output.mkdir(parents=True, exist_ok=True)

    try:
        config = AppConfig(spec=spec.resolve(), base_url=base_url, output=output.resolve())
        spec_document = load_openapi_spec(config.spec)
        spec_summary = extract_spec_summary(spec_document)
        test_suite = generate_test_suite(spec_summary)
        execution_summary = execute_test_suite(
            test_cases=test_suite.test_cases,
            base_url=config.base_url,
            timeout_seconds=config.timeout_seconds,
        )
        report_context = build_report_context(
            spec_file=str(config.spec),
            base_url=config.base_url,
            spec_summary=spec_summary,
            test_suite_summary=test_suite,
            execution_summary=execution_summary,
        )
        report_files = write_report_files(report_context, config.output)
    except (OpenAPILoaderError, SchemaResolverError, ValueError) as exc:
        console.print(f"[bold red]Execution setup error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    input_table = Table(title="Input Summary", show_header=False)
    input_table.add_column("Field", style="bold green")
    input_table.add_column("Value", style="white")
    input_table.add_row("Spec file", str(config.spec))
    input_table.add_row("Base URL", config.base_url)
    input_table.add_row("Output directory", str(config.output))
    input_table.add_row("Timeout (seconds)", str(config.timeout_seconds))
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

    execution_table = Table(title="Execution Summary")
    execution_table.add_column("Metric", style="bold magenta")
    execution_table.add_column("Value", style="white")
    execution_table.add_row("Total test cases", str(execution_summary.total_count))
    execution_table.add_row("Passed", str(execution_summary.passed_count))
    execution_table.add_row("Failed", str(execution_summary.failed_count))
    execution_table.add_row("Valid passed", str(execution_summary.valid_passed_count))
    execution_table.add_row("Invalid passed", str(execution_summary.invalid_passed_count))
    console.print(execution_table)

    preview_table = Table(title="Execution Result Preview (first 5)")
    preview_table.add_column("ID", style="bold cyan")
    preview_table.add_column("Status", style="green")
    preview_table.add_column("Method", style="white")
    preview_table.add_column("Path", style="white")
    preview_table.add_column("Expected", style="yellow")
    preview_table.add_column("Actual", style="yellow")
    preview_table.add_column("Error", style="red")

    for result in execution_summary.results[:5]:
        preview_table.add_row(
            result.test_id,
            "PASS" if result.passed else "FAIL",
            result.method,
            result.path,
            ", ".join(str(code) for code in result.expected_status_codes),
            str(result.actual_status_code) if result.actual_status_code is not None else "-",
            result.execution_error or ("; ".join(result.validation_errors) if result.validation_errors else "-"),
        )

    console.print(preview_table)

    report_table = Table(title="Generated Report Files")
    report_table.add_column("Format", style="bold cyan")
    report_table.add_column("Path", style="white")
    report_table.add_row("JSON", str(report_files["json"]))
    report_table.add_row("Markdown", str(report_files["markdown"]))
    report_table.add_row("HTML", str(report_files["html"]))
    console.print(report_table)

    if execution_summary.total_count > 0 and all(result.execution_error for result in execution_summary.results):
        console.print(
            "[bold yellow]Warning:[/bold yellow] All requests failed at transport level. "
            "If you run the tool inside Docker against an API on the host machine, remember that "
            "localhost inside the container is not always the host. Use host.docker.internal or a shared Docker network when needed."
        )

    console.print("[bold green]Test execution and report generation completed successfully.[/bold green]")


if __name__ == "__main__":
    app()
