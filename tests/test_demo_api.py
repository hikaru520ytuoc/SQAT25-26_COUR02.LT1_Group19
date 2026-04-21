import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo_api.app import app  # noqa: E402

client = TestClient(app)


def test_demo_api_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_api_get_user_success():
    response = client.get("/users/10", params={"includePosts": "true"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 10
    assert payload["username"] == "admin01"


def test_demo_api_post_user_validation_failure():
    response = client.post(
        "/users",
        json={
            "username": "",
            "email": "alice@example.com",
            "age": 10,
            "role": "member",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"message": "Validation failed"}
