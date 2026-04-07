# OpenAPI Test Tool

CLI tool skeleton for the project:

**“Xây dựng công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI”**

## Current status

This repository is currently in the **skeleton stage**.

Implemented in this stage:
- project structure
- CLI entrypoint
- local Python run
- Docker packaging
- Docker Compose demo run
- Makefile shortcuts
- sample OpenAPI file
- smoke test

Not implemented yet:
- real OpenAPI parsing
- automatic test case generation
- HTTP execution engine
- response validation
- report generation logic

---

## Project structure

```text
openapi-test-tool/
├── src/
│   └── openapi_test_tool/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── parser/
│       ├── generator/
│       ├── executor/
│       ├── reporter/
│       └── utils/
├── tests/
├── samples/
├── reports/
├── docs/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Requirements

- Ubuntu 24.04 LTS
- Python 3.12
- Docker
- Docker Compose

---

## Run locally

### 1. Create virtual environment and install dependencies

```bash
make install
```

### 2. Run CLI skeleton

```bash
make run
```

Or run manually:

```bash
PYTHONPATH=src .venv/bin/python main.py \
  --spec samples/sample_openapi.yaml \
  --base-url http://localhost:8000 \
  --output reports
```

---

## Run tests

```bash
make test
```

---

## Run with Docker

### Build image

```bash
make docker-build
```

### Run container

```bash
make docker-run
```

Or run manually:

```bash
docker run --rm -it \
  -v "$(pwd)/samples:/app/samples" \
  -v "$(pwd)/reports:/app/reports" \
  openapi-test-tool:dev \
  --spec samples/sample_openapi.yaml \
  --base-url http://localhost:8000 \
  --output reports
```

---

## Run with Docker Compose

Default demo command:

```bash
docker compose up --build
```

Run with custom arguments:

```bash
docker compose run --rm tool \
  --spec samples/sample_openapi.yaml \
  --base-url http://localhost:8000 \
  --output reports
```

---

## Makefile commands

```bash
make install
make run
make test
make docker-build
make docker-run
make clean
```

---

## Notes

- Docker is used here to package the CLI tool and make demo/setup easier.
- The current implementation only validates input arguments and prepares the output directory.
- Full business logic will be added in later milestones.
