SRC_PATH := frinx

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  test     run unit tests"
	@echo "  check    run ruff checks"
	@echo ""

.PHONY: check
check:
	poetry run ruff check $(SRC_PATH) --fix

.PHONY: test
test:
	poetry run pytest
