.PHONY: help init clean build test test-unit test-integration release upload-test upload-prod

# Default target
help:
	@echo "Available targets:"
	@echo "  init              - Initialize development environment"
	@echo "  clean             - Clean build artifacts"
	@echo "  build             - Build the package"
	@echo "  test              - Run all tests"
	@echo "  release           - Build and prepare for release"

# Initialize development environment
init:
	python -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -r requirements.txt
	@echo "Development environment initialized. Activate with: source .venv/bin/activate"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build the package
build: clean
	hatch build

# Run tests
test:
	python -m pytest tests/ -v --tb=short --cov=garmin_workouts_mcp --cov-report=term-missing

tests: test

lint:
	ruff check .

# Build and prepare for release
release: clean build
	@echo "Package built and ready for release"
	@echo "Files in dist/:"
	@ls -la dist/
	twine upload dist/*
