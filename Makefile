.PHONY: clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "format - format code"
	@echo "install - build and install everything"

build:
	poetry build

clean: clean-build

clean-build:
	rm -fr dist/

lint:
	poetry run black --check bxtctl
	pymarkdown scan .

format:
	poetry run black bxtctl
	pymarkdown fix .

unit-test:
	poetry shell && poetry run pytest

install: build
