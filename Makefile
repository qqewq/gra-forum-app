.PHONY: help install dev test clean run

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Install with dev dependencies"
	@echo "  make test     - Run tests"
	@echo "  make run      - Run default task"
	@echo "  make clean    - Clean temporary files"

install:
	pip install -r backend/requirements.txt
	pip install -e .

dev:
	pip install -r backend/requirements.txt
	pip install -e ".[dev]"

test:
	cd backend && pytest tests/ -v

run:
	python cli/run_software_task.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/