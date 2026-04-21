from __future__ import annotations

from openapi_test_tool.reporter.report_model import ReportContext


def build_json_report(context: ReportContext) -> dict:
    """Build a machine-readable JSON report payload."""

    return context.to_serializable_dict()
