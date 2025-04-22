.PHONY: install format lint test clean run

install:
	poetry install

format:
	poetry run black .
	poetry run ruff --fix .

lint:
	poetry run black . --check
	poetry run ruff check .
	poetry run mypy .

test:
	poetry run pytest tests/ -v --cov=src/blombo --cov-report=term-missing

clean:
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	poetry run uvicorn blombo.api.server:app --reload 