.PHONY: run test ci dev install install-editable uninstall fmt

dev:
	uv sync --group dev

run:
	uv run tc $(ARGS)

test:
	uv run pytest -v

fmt:
	uv run black .

ci:
	uv run black --check .
	uv run pyright

install:
	uv tool install .

install-editable:
	uv tool install --editable .

uninstall:
	uv tool uninstall tokencount
