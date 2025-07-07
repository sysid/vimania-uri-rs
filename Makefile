.DEFAULT_GOAL := help

SOURCEDIR     = source
BUILDDIR      = build
MAKE          = make
VERSION       = $(shell cat VERSION)

PYTEST	= pytest --log-level=debug --capture=tee-sys --asyncio-mode=auto
PYTOPT	=

VIM_PLUG="$(HOME)/dev/vim/tw-vim/config/plugins.vim"

app_root = $(PROJ_DIR)
app_root ?= .
pkg_src =  $(app_root)/pythonx/vimania_uri_rs
tests_src = $(app_root)/tests

# Makefile directory
CODE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: all
all: clean build upload tag  ## Build and upload
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"

################################################################################
# Developing \
DEVELOPING:  ## ###############################################################
.PHONY: setup
setup:  ## one-time development environment setup
	@echo "Setting up development environment..."
	uv sync
	uv run maturin develop
# 	uv run pre-commit install
	@echo "✅ Development environment ready!"

.PHONY: dev
dev: setup  ## setup environment and open IDE
	rustrover .

.PHONY: quick-dev
quick-dev:  ## fast development build (no confirmation)
	uv run maturin develop

.PHONY: check
check: quality security test-all  ## comprehensive check (quality + security + tests)

.PHONY: ci
ci: setup check  ## simulate CI pipeline locally

.PHONY: dev-vim
dev-vim:  ## open vim plugin and Makefile
	#vim -c 'OpenSession vimania-uri-rs'
	echo "not implemented"

.PHONY: _confirm
_confirm:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo "Action confirmed by user."

################################################################################
# Testing \
TESTING:  ## ##################################################################
.PHONY: test
test:  ## run tests
	PYTHONPATH=pythonx uv run pytest tests -vv

.PHONY: test-rust
test-rust:  ## run Rust tests
	cargo test --lib

.PHONY: test-all
test-all: test test-rust  ## run all tests (Python and Rust)

#.PHONY: test-vim
#test-vim:  test-vim-uri  ## run tests-vim

.PHONY: test-vim-uri
test-vim-uri: build-vim  ## run tests-vim-vimania (requires libs in pythonx: make build-vim)
	@echo "- > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > "
	pushd tests; ./run_test.sh test_vimania_uri.vader; popd
	@echo "- < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < "

################################################################################
# Building, Uploading \
BUILDING:  ## #################################################################
.PHONY: build-vim
build-vim: _confirm clean-vim ## clean and re-install via pip into pythonx
	python build.py --dev

.PHONY: clean-vim
clean-vim:  ## clean pythonx directory for PyCharm development
	@echo "Removing python packages from pythonx"
	@pushd pythonx; git clean -d -x -f; popd

.PHONY: requirements
requirements:  ## update dependencies with uv
	uv sync

.PHONY: vim-install
vim-install:  ## vim Plug install (external)
	sed -i.bkp "s#^\"Plug 'https://github.com/sysid/vimania-uri-rs.git'#Plug 'https://github.com/sysid/vimania-uri-rs.git'#" $(VIM_PLUG)
	sed -i.bkp "s#^Plug '~/dev/vim/vimania-uri-rs'#\"Plug '~/dev/vim/vimania-uri-rs'#" $(VIM_PLUG)
	vim -c ':PlugInstall vimania-uri-rs'

.PHONY: vim-uninstall
vim-uninstall:  ## vim Plug uninstall (use local)
	-[ -d "$(HOME)/.vim/plugged/vimania-uri-rs" ] && rm -fr "$(HOME)/.vim/plugged/vimania-uri-rs"
	sed -i.bkp "s#^\"Plug '~/dev/vim/vimania-uri-rs'#Plug '~/dev/vim/vimania-uri-rs'#" $(VIM_PLUG)
	sed -i.bkp "s#^Plug 'https://github.com/sysid/vimania-uri-rs.git'#\"Plug 'https://github.com/sysid/vimania-uri-rs.git'#" $(VIM_PLUG)
	#vim -c ':PlugClean vimania-uri-rs'

.PHONY: upload
upload:  ## upload to PyPi (now via CICD)
	@echo "upload"
	twine upload --verbose pythonx/dist/*


.PHONY: bump-major
bump-major:  check-github-token  ## bump-major, tag and push
	bump-my-version bump --commit --tag major
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: bump-minor
bump-minor:  check-github-token  ## bump-minor, tag and push
	bump-my-version bump --commit --tag minor
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: bump-patch
bump-patch:  check-github-token  ## bump-patch, tag and push
	bump-my-version bump --commit --tag patch
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: create-release
create-release: check-github-token  ## create a release on GitHub via the gh cli
	@if ! command -v gh &>/dev/null; then \
		echo "You do not have the GitHub CLI (gh) installed. Please create the release manually."; \
		exit 1; \
	else \
		echo "Creating GitHub release for v$(VERSION)"; \
		gh release create "v$(VERSION)" --generate-notes --latest; \
	fi

.PHONY: create-release
create-release:  ## create a release on GitHub via the gh cli
	@if command -v gh version &>/dev/null; then \
		echo "Creating GitHub release for v$(VERSION)"; \
		gh release create "v$(VERSION)" --generate-notes; \
	else \
		echo "You do not have the github-cli installed. Please create release from the repo manually."; \
		exit 1; \
	fi

.PHONY: check-github-token
check-github-token:  ## Check if GITHUB_TOKEN is set
	@if [ -z "$$GITHUB_TOKEN" ]; then \
		echo "GITHUB_TOKEN is not set. Please export your GitHub token before running this command."; \
		exit 1; \
	fi
	@echo "GITHUB_TOKEN is set"
	#@$(MAKE) fix-version  # not working: rustrover deleay


.PHONY: fix-version
fix-version:  ## fix-version of Cargo.toml, re-connect with HEAD
	git add rsenv/Cargo.lock
	git commit --amend --no-edit
	git tag -f "v$(VERSION)"
	git push --force-with-lease
	git push --tags --force

################################################################################
# Quality \
QUALITY:  ## ##################################################################

.PHONY: format
format:  ## perform ruff formatting
	@uv run ruff format $(pkg_src) $(tests_src)

.PHONY: format-check
format-check:  ## check ruff formatting
	@uv run ruff format --check $(pkg_src) $(tests_src)

.PHONY: sort-imports
sort-imports:  ## apply import sort ordering
	uv run isort $(pkg_src) $(tests_src) --profile black

.PHONY: style
style: sort-imports format  ## perform code style format (ruff, isort)

.PHONY: lint
lint:  ## check style with ruff
	uv run ruff check $(pkg_src) $(tests_src)

.PHONY: mypy
mypy:  ## check type hint annotations
	@uv run mypy --config-file pyproject.toml --install-types --non-interactive $(pkg_src)

.PHONY: rust-format
rust-format:  ## format Rust code
	cargo fmt

.PHONY: rust-lint
rust-lint:  ## lint Rust code
	cargo clippy -- -D warnings

.PHONY: rust-check
rust-check:  ## check Rust code compiles
	cargo check

.PHONY: quality
quality: lint mypy format-check rust-lint  ## run all quality checks

.PHONY: quality-fix
quality-fix: style rust-format  ## fix all auto-fixable quality issues

.PHONY: security
security:  ## run security checks
	uv run bandit -r $(pkg_src)
	cargo audit

.PHONY: pre-commit
pre-commit:  ## run pre-commit hooks on all files
	uv run pre-commit run --all-files

.PHONY: pre-commit-update
pre-commit-update:  ## update pre-commit hooks
	uv run pre-commit autoupdate


################################################################################
# Clean \
CLEAN:  ## #################################################################
.PHONY: clean
clean: clean-build clean-pyc  ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +


################################################################################
# Misc \
MISC:  ## ############################################################

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([%a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		if target != "dummy":
			print("\033[36m%-20s\033[0m %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
