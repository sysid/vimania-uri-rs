# Installation Guide

This guide covers the installation of the vimania-uri-rs Vim plugin, which provides advanced URI handling capabilities with Rust performance.

## Prerequisites

- Vim with Python3 support (check with `:echo has('python3')` in Vim)
- Rust toolchain (for building the extension module)
- Python 3.10 or higher
- `maturin` for building Python extensions from Rust

## Installation Steps

### 1. Install Rust Dependencies

```bash
# Install maturin if not already installed
pip install maturin
```

### 2. Build and Install the Rust Extension Module

The plugin requires a Rust extension module (`vimania_uri_rs`) to be available in your system Python. This is the most critical step:

```bash
# From the project root directory

# Option A: Build and install in one step (if your system allows it)
pip install -e .

# Option B: Build wheel and install manually (for externally-managed environments)
maturin build --release
pip install --break-system-packages target/wheels/vimania_uri_rs-*.whl

# Option C: For Homebrew Python specifically
/opt/homebrew/bin/python3 -m pip install --break-system-packages target/wheels/vimania_uri_rs-*.whl
```

This will:
- Build the Rust extension module using maturin
- Install it to your system Python
- Make it available to Vim's Python interpreter

**Note**: This step is essential because Vim's Python interpreter needs access to the `vimania_uri_rs` module. The module must be installed in the same Python environment that Vim uses (usually Homebrew Python on macOS).

### 3. Install the Vim Plugin

Copy or symlink the plugin files to your Vim configuration:

#### Option A: Manual Installation

```bash
# Copy plugin files to your Vim plugin directory
cp plugin/vimania_uri_rs.vim ~/.vim/plugin/
cp plugin/vimania_uri_rs.py ~/.vim/plugin/

# Copy Python modules to your Vim pythonx directory
cp -r pythonx/vimania_uri_ ~/.vim/pythonx/
```

#### Option B: Using a Plugin Manager

Add this repository to your preferred Vim plugin manager (vim-plug, Vundle, etc.):

```vim
" Example for vim-plug
Plug 'sysid/vimania-uri-rs'
```

### 4. Verify Installation

1. Start Vim
2. The plugin should load without errors
3. Test with a markdown file containing URIs

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'vimania_uri_rs'

This error occurs when the Rust extension module is not properly installed in the system Python that Vim uses.

**Solution**: Ensure you've run `pip install -e .` from the project root directory. This installs the module system-wide, making it available to Vim's Python interpreter.

#### Virtual Environment Issues

If you're working in a virtual environment but Vim can't find the module:

1. Activate your virtual environment
2. Run `pip install -e .` to install the module
3. If the issue persists, install to system Python: `deactivate && pip install -e .`

#### Python Path Issues

Verify that Vim is using the correct Python:

```vim
:py3 import sys; print(sys.executable)
:py3 import sys; print(sys.path)
```

### Development Installation

For development work:

```bash
# Install in development mode with editable installation
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt  # if available
```

### Uninstallation

To remove the plugin:

```bash
# Remove the Python module
pip uninstall vimania_uri_rs

# Remove plugin files
rm ~/.vim/plugin/vimania_uri_rs.vim
rm ~/.vim/plugin/vimania_uri_rs.py
rm -rf ~/.vim/pythonx/vimania_uri_
```

## Configuration

After installation, you can configure the plugin by setting variables in your `.vimrc`:

```vim
" Supported file extensions for URI handling
let g:vimania_uri_extensions = ['.md', '.txt', '.rst', '.py', '.conf', '.sh', '.json', '.yaml', '.yml']

" Vim split policy (none, horizontal, vertical)
let g:vimania_uri_rs_default_vim_split_policy = "none"
```