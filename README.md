# OpenAPI Test Tool

CLI tool for the project:

**“Xây dựng công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI”**

## Current status

This repository is currently in the **executor stage**.

Implemented in this stage:
- OpenAPI loader and parser for OpenAPI 3.x at MVP level
- internal models for endpoints and parsed spec metadata
- automatic functional test case generation
- HTTP request execution with `requests`
- status code validation
- basic response schema validation with `jsonschema`
- CLI summary for parsing, generation, and execution
- Docker packaging and Docker Compose demo run
- pytest suite for parser, generator, executor, and CLI

Not implemented yet:
- HTML/JSON report writer for final result export
- advanced authentication flows
- stateful workflow execution across multiple endpoints
- async execution or performance testing

---

## Project structure

```text
openapi-test-tool/
├── src/
│   └── openapi_test_tool/
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

### 2. Run the CLI

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
docker run --rm -it \
  -v "$(pwd)/samples:/app/samples" \
  -v "$(pwd)/reports:/app/reports" \
  openapi-test-tool:dev \
  --spec samples/sample_openapi.yaml \
  --base-url http://host.docker.internal:8000 \
  --output reports
```

### Important Docker note

If the tool runs **inside Docker** and your API runs **on the host machine**, `localhost` inside the container is not always the same as the host machine.

Common options:
- use `host.docker.internal`
- or run both services in the same Docker Compose network

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
  --base-url http://host.docker.internal:8000 \
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
