.PHONY: run test ci install

install:
	uv sync --group dev

run:
	uv run tc $(ARGS)

test:
	uv run pytest -v

ci:
	uv run black --check .
	uv run pyright
