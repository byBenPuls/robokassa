.PHONY: all

SHELL=/bin/bash -e

format:
	poetry run ruff format .
	poetry run ruff check --fix .

test:
	poetry run pytest . -p no:logging -p no:warnings

build:
	poetry build

publish:
	poetry publish

update:
	poetry update

release:
	poetry version $(version)
