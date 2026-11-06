.PHONY: help build run test demo clean docker-test

help:
	@echo "Vesper Engine — Systems Automation Commands"
	@echo "  make build       - Build the isolated Docker sandbox runtime image"
	@echo "  make run         - Launch the FastAPI interactive studio server"
	@echo "  make demo        - Execute multi-language benchmark showcase"
	@echo "  make test        - Run complete Pytest suite (AC, WA, TLE, MLE, RE, CE, OLE)"
	@echo "  make docker-test - Run automated tests inside containerized sandbox"
	@echo "  make clean       - Remove cached artifacts, pycache, and ephemeral volumes"

build:
	docker build -t vesper-sandbox:latest -f src/judger_dockerfile/Dockerfile .

run:
	python server.py

demo:
	python demo.py

test:
	python -m pytest -v

docker-test:
	docker run --rm -v $$(pwd):/app -w /app vesper-sandbox:latest pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
