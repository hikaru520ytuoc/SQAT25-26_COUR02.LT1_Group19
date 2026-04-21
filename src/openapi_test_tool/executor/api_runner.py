from __future__ import annotations

from typing import Any

import requests

from openapi_test_tool.executor.execution_model import BuiltRequest, RawExecutionResponse


DEFAULT_TIMEOUT_SECONDS = 10


def send_request(built_request: BuiltRequest, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> RawExecutionResponse:
    """Execute one HTTP request and capture transport-level outputs."""

    try:
        response = requests.request(
            method=built_request.method,
            url=built_request.url,
            params=built_request.query_params,
            headers=built_request.headers,
            json=built_request.json_body,
            timeout=timeout_seconds,
        )
    except requests.exceptions.Timeout as exc:
        return RawExecutionResponse(execution_error=f"Request timed out: {exc}")
    except requests.exceptions.ConnectionError as exc:
        return RawExecutionResponse(execution_error=f"Connection error: {exc}")
    except requests.exceptions.InvalidURL as exc:
        return RawExecutionResponse(execution_error=f"Invalid URL: {exc}")
    except requests.exceptions.RequestException as exc:
        return RawExecutionResponse(execution_error=f"Request failed: {exc}")

    return RawExecutionResponse(
        actual_status_code=response.status_code,
        response_headers=dict(response.headers),
        response_body=_extract_response_body(response),
        response_time_ms=_extract_elapsed_ms(response),
    )


def _extract_response_body(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text_body = response.text
        return text_body if text_body != "" else None


def _extract_elapsed_ms(response: requests.Response) -> float | None:
    elapsed = getattr(response, "elapsed", None)
    if elapsed is None:
        return None

    total_seconds = getattr(elapsed, "total_seconds", None)
    if callable(total_seconds):
        return round(total_seconds() * 1000, 3)
    return None
