from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import Body, FastAPI, Header, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class UserRecord(BaseModel):
    id: int
    username: str = Field(..., min_length=3, max_length=20)
    email: str
    age: int = Field(..., ge=18, le=120)
    role: UserRole


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., min_length=3, max_length=20)
    email: str
    age: int = Field(..., ge=18, le=120)
    role: UserRole


class ErrorResponse(BaseModel):
    message: str


app = FastAPI(
    title="Demo User API",
    version="0.1.0",
    description="Minimal in-memory API used to demonstrate the OpenAPI test tool executor.",
)


USERS: dict[int, UserRecord] = {
    10: UserRecord(id=10, username="admin01", email="admin@example.com", age=30, role=UserRole.ADMIN),
}
NEXT_USER_ID = 11


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    _ = request, exc
    return JSONResponse(status_code=422, content={"message": "Validation failed"})


@app.get(
    "/health",
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/users/{userId}",
    response_model=UserRecord,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def get_user(
    userId: int = Path(..., ge=1),
    includePosts: bool = Query(False),
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> dict[str, Any]:
    _ = includePosts, x_trace_id

    user = USERS.get(userId)
    if user is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    return user.model_dump()


@app.post(
    "/users",
    response_model=UserRecord,
    status_code=201,
    responses={422: {"model": ErrorResponse}},
)
def create_user(payload: CreateUserRequest = Body(...)) -> dict[str, Any]:
    global NEXT_USER_ID

    user = UserRecord(id=NEXT_USER_ID, **payload.model_dump())
    USERS[NEXT_USER_ID] = user
    NEXT_USER_ID += 1
    return user.model_dump()
