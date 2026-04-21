from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from openapi_test_tool.reporter.report_model import ReportContext

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def build_html_report(context: ReportContext) -> str:
    """Render a lightweight HTML report for demos."""

    environment = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template("report.html.j2")
    return template.render(
        context=context,
        pretty_json=_pretty_json,
        pass_label="PASS",
        fail_label="FAIL",
    )


def _pretty_json(value) -> str:
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)
