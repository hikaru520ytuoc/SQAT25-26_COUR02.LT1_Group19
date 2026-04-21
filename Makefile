PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
PYRUN := PYTHONPATH=src $(VENV)/bin/python

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYRUN) main.py --spec samples/sample_openapi.yaml --base-url http://localhost:8000 --output reports

test:
	PYTHONPATH=src $(PYTEST) -q

docker-build:
	docker build -t openapi-test-tool:dev .

docker-run:
	docker run --rm -it \
		-v $(PWD)/samples:/app/samples \
		-v $(PWD)/reports:/app/reports \
		openapi-test-tool:dev \
		--spec samples/sample_openapi.yaml \
		--base-url http://localhost:8000 \
		--output reports

clean:
	rm -rf $(VENV) .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find reports -mindepth 1 -not -name ".gitkeep" -delete
