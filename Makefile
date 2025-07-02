.PHONY: help init clean build test release upload-test upload-prod

# Default target
help:
	@echo "Available targets:"
	@echo "  init        - Initialize development environment"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the package"
	@echo "  test        - Run tests (if any)"
	@echo "  release     - Build and prepare for release"
	@echo "  upload-test - Upload to TestPyPI"
	@echo "  upload-prod - Upload to PyPI"

# Initialize development environment
init:
	python -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -r requirements.txt

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

# Run tests (placeholder for when tests are added)
test:
	@echo "No tests configured yet"

# Build and prepare for release
release: clean build
	@echo "Package built and ready for release"
	@echo "Files in dist/:"
	@ls -la dist/
	twine upload dist/*
