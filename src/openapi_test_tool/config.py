from pathlib import Path

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Runtime configuration for the CLI tool."""

    spec: Path
    base_url: str = Field(..., min_length=1)
    output: Path = Path("reports")
    timeout_seconds: int = Field(default=10, ge=1, le=120)
