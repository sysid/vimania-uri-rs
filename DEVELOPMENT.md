# Development Guide

This document provides detailed guidance for developing the vimania-uri-rs plugin, covering both Python and Rust development workflows.

## Prerequisites

### Required Tools
- **Python 3.10+** with pip
- **Rust** with Cargo
- **uv** (Python package manager)
- **maturin** (Rust-Python build tool)
- **Vim/Neovim** for plugin testing

### Optional Tools
- **RustRover** IDE with Python plugin (recommended)
- **make** for convenient command shortcuts

## Project Structure Overview

```
vimania-uri-rs/
├── src/                    # Rust source code
│   ├── lib.rs             # PyO3 bindings (main Rust module)
│   └── main.rs            # Rust executable (if needed)
├── pythonx/               # Python packages for Vim
│   ├── vimania_uri_/      # Main Python plugin code
│   └── vimania_uri_rs/    # Built Rust extension (auto-generated)
├── plugin/                # Vim plugin files
├── tests/                 # Test files (Python, Rust, Vim)
├── target/                # Rust build artifacts
└── build.py               # Custom build script
```

## Development Workflows

### 1. Python Development

#### Initial Setup
```bash
# Install Python dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

#### Development Environment
The Python code lives in `pythonx/vimania_uri_/` and includes:
- `mdnav.py`: Markdown navigation and link parsing
- `vim_/vimania_manager.py`: Main plugin logic
- `bms/handler.py`: Bookmark manager integration
- `environment.py`: Configuration management

#### Python Development Commands
```bash
# Run Python tests
make test
# or manually:
PYTHONPATH=pythonx python -m pytest tests -vv

# Lint Python code
make lint
# or manually:
ruff check pythonx/vimania_uri_rs tests

# Format Python code
make format
# or manually:
ruff format pythonx/vimania_uri_rs tests

# Sort imports
make sort-imports
# or manually:
isort pythonx/vimania_uri_rs tests --profile black

# Type checking
make mypy
# or manually:
mypy --config-file pyproject.toml pythonx/vimania_uri_rs

# All style checks at once
make style
```

#### Python Development Notes
- Use `PYTHONPATH=pythonx` when running tests to ensure proper imports
- The plugin expects all packages to be in `pythonx/` directory
- Environment variables:
  - `LOG_LEVEL`: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR)
  - `BKMR_DB_URL`: Database URL for bookmark manager integration

### 2. Rust Development

#### Initial Setup
```bash
# Ensure Rust is installed
cargo --version

# Install maturin if not already installed
pip install maturin
```

#### Rust Development Environment
The Rust code in `src/lib.rs` provides:
- PyO3 bindings for Python integration
- High-performance URL title fetching
- HTML parsing and processing
- HTTP client functionality

#### Rust Development Commands
```bash
# Build Rust extension (development mode)
python build.py --dev

# Build Rust extension (release mode)
python build.py

# Run Rust tests only
make test-rust
# or manually:
cargo test --lib

# Check Rust code
cargo check

# Format Rust code
cargo fmt

# Lint Rust code
cargo clippy
```

#### Rust Development Notes
- The Rust crate must be compiled with the same Python version as Vim
- PyO3 features are enabled: `extension-module`, `anyhow`
- Development builds include debug symbols and logging
- The built `.so` file is automatically installed to `pythonx/vimania_uri_rs/`

### 3. Hybrid Development (Python + Rust)

#### Full Development Setup
```bash
# 1. Clean previous builds
make clean-vim

# 2. Build and install for development
make build-vim
# This runs: python build.py --dev
```

#### Development Cycle
1. **Make changes** to Python code in `pythonx/vimania_uri_/`
2. **Make changes** to Rust code in `src/lib.rs`
3. **Rebuild** the extension: `python build.py --dev`
4. **Test** the changes: `make test` or `make test-vim-uri`
5. **Repeat** as needed

#### Important Build Notes
- `make build-vim` requires confirmation (safety measure)
- Development builds are faster but larger
- Release builds are optimized for production
- The build script handles wheel creation and installation automatically

## Testing

### Python Tests
```bash
# Run all Python tests
make test

# Run specific test file
PYTHONPATH=pythonx python -m pytest tests/test_pattern.py -v

# Run with debugging
PYTHONPATH=pythonx python -m pytest tests -vv --log-level=DEBUG
```

### Rust Tests
```bash
# Run Rust unit tests
make test-rust

# Run specific Rust test
cargo test specific_test_name
```

### Vim Plugin Tests
```bash
# Run Vim integration tests (requires build-vim first)
make test-vim-uri

# Manual vim test
vim -c ':source plugin/vimania_uri_rs.vim' -c ':echo "Plugin loaded"'
```

## IDE Configuration

### RustRover (Recommended)
```bash
# Open project in RustRover
make dev
# or manually:
rustrover .
```

**RustRover Setup:**
1. Install Python plugin
2. Configure Python interpreter to point to `.venv/bin/python`
3. Set working directory to project root
4. Enable Rust and Python support

### VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "rust-analyzer.checkOnSave.command": "clippy"
}
```

## Vim Plugin Development

### Local Development Setup
Add to your Vim configuration:
```vim
" For local development
Plug '~/path/to/vimania-uri-rs'

" Configuration
let g:vimania_uri_extensions=['.md', '.txt', '.py']
let g:vimania_uri_twbm_integration=1  " if bkmr is installed
```

### Plugin Installation for Testing
```bash
# Install as external plugin
make vim-install

# Uninstall and use local version
make vim-uninstall
```

## Environment Variables

### Required for Development
- `PYTHONPATH=pythonx`: For running tests and development

### Optional Configuration
- `LOG_LEVEL`: Set to `DEBUG` for verbose logging
- `BKMR_DB_URL`: Database URL for bookmark manager integration

## Troubleshooting

### Common Issues

1. **Wrong Python version for Rust extension**
   - Ensure Rust is compiled with same Python version as Vim
   - Check: `python --version` vs Vim's Python version

2. **Import errors in tests**
   - Always use `PYTHONPATH=pythonx` when running tests
   - Ensure `make build-vim` was run successfully

3. **Vim plugin not loading**
   - Check that `pythonx/vimania_uri_rs/` contains the `.so` file
   - Verify Vim has `+python3` support: `:python3 import sys; print(sys.version)`

4. **Build failures**
   - Clean builds: `make clean-vim && make build-vim`
   - Check Rust/Cargo installation: `cargo --version`
   - Ensure maturin is installed: `pip install maturin`

### Debug Information
```bash
# Check Python environment
python -c "import sys; print(sys.path)"

# Check Rust compilation
cargo check --verbose

# Test Rust-Python integration
python -c "import vimania_uri_rs; print('OK')"
```

## Release Process

### Version Management
```bash
# Bump version (patch/minor/major)
make bump-patch  # Creates commit, tag, and GitHub release

# Manual version update
# Edit: VERSION, pyproject.toml, Cargo.toml
```

### Quality Assurance
```bash
# Run all checks before release
make style
make lint
make mypy
make test
make test-rust
```

## Make Target Reference

### Development
- `make dev`: Open RustRover IDE
- `make build-vim`: Build and install for Vim development
- `make clean-vim`: Clean pythonx directory

### Testing
- `make test`: Run Python tests
- `make test-rust`: Run Rust tests
- `make test-vim-uri`: Run Vim plugin tests

### Code Quality
- `make lint`: Check Python code style
- `make format`: Format Python code
- `make mypy`: Type checking
- `make style`: Format and sort imports

### Build & Release
- `make clean`: Remove all build artifacts
- `make bump-patch/minor/major`: Version bump and release