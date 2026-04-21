import sys
from pathlib import Path

from typer.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.cli import app  # noqa: E402

runner = CliRunner()


def test_cli_smoke_creates_output_dir(tmp_path):
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    output_dir = tmp_path / "reports"

    result = runner.invoke(
        app,
        [
            "--spec",
            str(spec_path),
            "--base-url",
            "http://localhost:8000",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert output_dir.exists()
    assert "Test case generation completed successfully." in result.stdout
