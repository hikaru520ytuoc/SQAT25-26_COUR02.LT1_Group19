# OpenAPI Test Tool

CLI tool for the project:

**“Xây dựng công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI”**

## Current status

This repository is currently in **stage 5.5**.

Implemented in this stage:
- OpenAPI loader and parser for OpenAPI 3.x at MVP level
- internal models for endpoints and parsed spec metadata
- automatic functional test case generation
- HTTP request execution with `requests`
- status code validation
- basic response schema validation with `jsonschema`
- lightweight local demo API with FastAPI
- local run and Docker Compose demo flow for `tool -> demo API`
- pytest suite for parser, generator, executor, CLI, and demo API

Not implemented yet:
- detailed report writer to JSON/HTML files
- advanced authentication flows
- multi-step workflow execution across endpoints
- async execution or performance testing

---

## Project structure

```text
openapi-test-tool/
├── demo_api/
│   ├── __init__.py
│   └── app.py
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

## Local demo flow

### 1. Install dependencies

```bash
make install
```

### 2. Start the local demo API

```bash
make demo-api
```

The demo API will run at:

```text
http://localhost:8000
```

Available demo endpoints:
- `GET /health`
- `GET /users/{userId}`
- `POST /users`

### 3. Run the OpenAPI test tool against the demo API

In another terminal:

```bash
make run
```

Or manually:

```bash
PYTHONPATH=src:. .venv/bin/python main.py \
  --spec samples/sample_openapi.yaml \
  --base-url http://localhost:8000 \
  --output reports
```

---

## Docker Compose demo flow

### 1. Start the demo API container

```bash
make demo-up
```

### 2. Run the tool container against the demo API container

```bash
make demo-run
```

This uses the internal Compose network, so the tool reaches the API at:

```text
http://demo-api:8000
```

### 3. Stop the demo environment

```bash
make demo-down
```

---

## Run the tool in plain Docker against a host API

Build image:

```bash
make docker-build
```

Run tool container:

```bash
docker run --rm -it \
  --add-host host.docker.internal:host-gateway \
  -v "$(pwd)/samples:/app/samples" \
  -v "$(pwd)/reports:/app/reports" \
  openapi-test-tool:dev \
  --spec samples/sample_openapi.yaml \
  --base-url http://host.docker.internal:8000 \
  --output reports
```

### Important Docker note

If the tool runs **inside Docker** and the API runs **on your Ubuntu host**, `localhost` inside the container is not the host machine.

Use one of these options:
- `http://host.docker.internal:8000`
- or run both containers in the same Docker Compose network

---

## Run tests

```bash
make test
```

---

## Expected demo behavior

When the demo API is running, the tool should now produce a realistic execution summary:
- some test cases pass
- some test cases fail in a meaningful way
- response status codes are real
- response bodies are real JSON
- schema validation runs on real responses

This is enough to demonstrate that the project can:
- parse OpenAPI
- generate test cases
- execute real HTTP requests
- validate responses against expected behavior

---

## Makefile commands

```bash
make install
make run
make demo-api
make test
make docker-build
make docker-run
make demo-up
make demo-run
make demo-down
make clean
```
