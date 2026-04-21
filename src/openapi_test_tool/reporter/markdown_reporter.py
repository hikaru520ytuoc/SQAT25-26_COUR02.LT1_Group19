from __future__ import annotations

import json
from typing import Any

from openapi_test_tool.reporter.report_model import ReportContext


def build_markdown_report(context: ReportContext) -> str:
    """Render a simple Markdown report for README/demo/report usage."""

    lines: list[str] = []
    lines.append("# OpenAPI Test Tool Execution Report")
    lines.append("")
    lines.append(f"- **Generated at:** {context.summary.generated_at}")
    lines.append(f"- **Spec file:** `{context.spec_file}`")
    lines.append(f"- **Base URL:** `{context.base_url}`")
    lines.append("")

    lines.append("## Spec Metadata")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| OpenAPI version | {context.spec_summary.openapi_version} |")
    lines.append(f"| Title | {context.spec_summary.title or '-'} |")
    lines.append(f"| Spec version | {context.spec_summary.version or '-'} |")
    lines.append(f"| Path count | {context.spec_summary.path_count} |")
    lines.append(f"| Operation count | {context.spec_summary.operation_count} |")
    lines.append("")

    lines.append("## Execution Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Total test cases | {context.summary.total_test_cases} |")
    lines.append(f"| Generated valid cases | {context.summary.generated_valid_count} |")
    lines.append(f"| Generated invalid cases | {context.summary.generated_invalid_count} |")
    lines.append(f"| Passed | {context.summary.passed_count} |")
    lines.append(f"| Failed | {context.summary.failed_count} |")
    lines.append(f"| Valid passed | {context.summary.valid_passed_count} |")
    lines.append(f"| Invalid passed | {context.summary.invalid_passed_count} |")
    lines.append("")

    lines.append("## Detailed Results")
    lines.append("")
    lines.append("| ID | PASS/FAIL | Category | Type | Method | Path | Expected | Actual |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for result in context.detailed_results:
        lines.append(
            f"| {result.test_id} | {'PASS' if result.passed else 'FAIL'} | {result.category.value} | "
            f"{result.test_type.value} | {result.method} | `{result.path}` | "
            f"{', '.join(str(code) for code in result.expected_status_codes)} | "
            f"{result.actual_status_code if result.actual_status_code is not None else '-'} |"
        )
    lines.append("")

    failed_results = [result for result in context.detailed_results if not result.passed]
    if failed_results:
        lines.append("## Failed Cases")
        lines.append("")
        for result in failed_results:
            lines.append(f"### {result.test_id} - {result.name}")
            lines.append("")
            lines.append(f"- **Method:** {result.method}")
            lines.append(f"- **Path:** `{result.path}`")
            lines.append(f"- **Expected status:** {', '.join(str(code) for code in result.expected_status_codes)}")
            lines.append(f"- **Actual status:** {result.actual_status_code if result.actual_status_code is not None else '-'}")
            if result.execution_error:
                lines.append(f"- **Execution error:** {result.execution_error}")
            if result.validation_errors:
                lines.append(f"- **Validation errors:** {'; '.join(result.validation_errors)}")
            if result.response_body is not None:
                lines.append("- **Response body:**")
                lines.append("")
                lines.append("```json")
                lines.append(_format_json_like(result.response_body))
                lines.append("```")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def _format_json_like(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)
