# NetForge developer entry points. Run `make help` for a summary.

# The lab gets its own Colima VM so timing measurements don't share CPU with
# other projects. Selecting the context per-command (instead of `docker context
# use`) leaves the user's global Docker context untouched. Override for Linux/CI:
#   make doctor NETFORGE_DOCKER_CONTEXT=default
NETFORGE_DOCKER_CONTEXT ?= colima-netforge
export DOCKER_CONTEXT := $(NETFORGE_DOCKER_CONTEXT)

UV ?= uv

.DEFAULT_GOAL := help
.PHONY: help sync fmt fmt-check lint typecheck test test-integration check doctor \
        vm-up vm-down vm-status clean

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync: ## Install the locked Python environment
	$(UV) sync --locked

fmt: ## Auto-format and apply safe lint fixes
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

fmt-check: ## Verify formatting without changing files
	$(UV) run ruff format --check .

lint: ## Lint Python (ruff) and shell scripts (shellcheck)
	$(UV) run ruff check .
	shellcheck scripts/*.sh

typecheck: ## Static type check with mypy (strict)
	$(UV) run mypy

test: ## Run unit tests (no Docker required)
	$(UV) run pytest tests/unit

test-integration: ## Run tests that need a Docker daemon
	$(UV) run pytest -m integration tests/integration

check: fmt-check lint typecheck test ## Everything CI runs on every push

doctor: ## Check Python, Docker daemon, kernel and VM sizing
	$(UV) run netforge-doctor --expect-context $(NETFORGE_DOCKER_CONTEXT)

vm-up: ## Start (or create) the dedicated netforge Colima VM
	./scripts/colima-netforge.sh up

vm-down: ## Stop the netforge Colima VM
	./scripts/colima-netforge.sh down

vm-status: ## Show the netforge Colima VM status
	./scripts/colima-netforge.sh status

clean: ## Remove caches and build output
	rm -rf .mypy_cache .pytest_cache .ruff_cache dist build
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
