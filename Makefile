PKG_NAME      := tg-proxy
PKG_DIR_NAME  := tg_proxy
PKG_DIR       := src/$(PKG_DIR_NAME)
VERSION       := $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d= -f2 | xargs)

# System Paths
REAL_USER := $(if $(SUDO_USER),$(SUDO_USER),$(USER))
REAL_HOME := $(shell getent passwd $(REAL_USER) | cut -d: -f6)
BIN_DIR   := $(REAL_HOME)/.local/bin

# Tooling
UV     := $(shell command -v uv 2>/dev/null || echo uv)
PYTHON := $(UV) run python
PYTEST := $(PYTHON) -m pytest

PY_FILES := $(shell find $(PKG_DIR) -name "*.py")

.PHONY: help check uv-install uv-link uv-uninstall uv-purge uv-build uv-publish git-push release docker-build docker-publish docker-logs git-install-hooks

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*##"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Quality ───

check: ## Run all checks (ruff lint+fix + ruff format + py_compile + pyright + pytest)
	@$(UV) run ruff check --fix $(PKG_DIR)/
	@$(UV) run ruff format $(PKG_DIR)/
	@$(PYTHON) -m py_compile $(PY_FILES)
	@$(UV) run pyright $(PKG_DIR)/
	@$(PYTHON) -m pytest tests/ -v

# ─── Install / Uninstall (uv tool) ───

uv-install: ## Install via uv tool
	@$(UV) tool install . --force
	@echo "✅ $(PKG_NAME) installed"

uv-link: ## Install editable (dev)
	@$(UV) tool install --editable . --force
	@echo "✅ $(PKG_NAME) linked (editable)"

uv-uninstall: ## Uninstall uv tool
	@$(UV) tool uninstall $(PKG_NAME) 2>/dev/null || true
	@echo "✅ $(PKG_NAME) uninstalled"

uv-purge: uv-uninstall ## Full purge
	@rm -rf dist/ build/ *.egg-info
	@echo "✅ $(PKG_NAME) purged"

# ─── Build / Publish ───

uv-build: ## Build Python sdist and wheel
	@echo "🏗️  Building Python package v$(VERSION)..."
	@rm -rf dist/
	@$(UV) build

uv-publish: uv-build ## Publish to PyPI
	@echo "🚀 Publishing v$(VERSION) to PyPI..."
	@$(UV) publish

# ─── Git ───

git-push: ## Push to both gitlab and github
	@git push github main
	@git push gitlab main
	@echo "✅ Pushed to github + gitlab"

git-install-hooks: ## Install pre-commit hook
	@echo "#!/bin/sh\nmake check" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed"

# ─── Release ───

release: check git-push uv-publish docker-publish ## Full release: check → push → publish → docker

# ─── Docker ───

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image kpihx/$(PKG_NAME)..."
	@docker build -t kpihx/$(PKG_NAME):latest .

docker-publish: ## Push Docker image
	@docker push kpihx/$(PKG_NAME):latest

docker-logs: ## View logs
	@docker logs tg-proxy 2>/dev/null || echo "No container running"
