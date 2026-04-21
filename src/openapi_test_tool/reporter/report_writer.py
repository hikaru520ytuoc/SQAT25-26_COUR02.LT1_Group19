from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from openapi_test_tool.reporter.html_reporter import build_html_report
from openapi_test_tool.reporter.json_reporter import build_json_report
from openapi_test_tool.reporter.markdown_reporter import build_markdown_report
from openapi_test_tool.reporter.report_model import ReportContext


def write_report_files(
    context: ReportContext,
    output_dir: str | Path,
    timestamp: str | None = None,
) -> dict[str, Path]:
    """Write JSON, Markdown, and HTML reports to the output directory."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    suffix = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"report_{suffix}"

    json_path = output_path / f"{base_name}.json"
    markdown_path = output_path / f"{base_name}.md"
    html_path = output_path / f"{base_name}.html"

    json_path.write_text(
        json.dumps(build_json_report(context), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown_path.write_text(build_markdown_report(context), encoding="utf-8")
    html_path.write_text(build_html_report(context), encoding="utf-8")

    return {
        "json": json_path,
        "markdown": markdown_path,
        "html": html_path,
    }
