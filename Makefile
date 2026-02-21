.PHONY: install test run-experiments run-api docker-build docker-up docker-down clean

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

run-experiments:
	python run_experiments.py

run-api:
	python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	rm -rf results/*
	rm -rf __pycache__ src/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	find . -type f -name "*.pyc" -delete

reproduce: install run-experiments
	@echo "Experiments complete! Check results/experiment_results.json"

all: install run-experiments
