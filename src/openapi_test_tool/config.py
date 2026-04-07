from pathlib import Path

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Runtime configuration for the CLI skeleton."""

    spec: Path
    base_url: str = Field(..., min_length=1)
    output: Path = Path("reports")
