# API Documentation

This document provides detailed information about the vimania-uri-rs plugin's API, configuration options, and integration points.

## Table of Contents

- [Plugin Interface](#plugin-interface)
- [Python API](#python-api)
- [Rust API](#rust-api)
- [Configuration Reference](#configuration-reference)
- [Integration Hooks](#integration-hooks)
- [Error Handling](#error-handling)

## Plugin Interface

### Core Commands

#### `<Plug>vimania_uri_go`
The main command for URI navigation.

**Usage:**
```vim
" Default mapping
nmap go <Plug>vimania_uri_go

" Custom mapping
nmap <leader>u <Plug>vimania_uri_go
```

**Behavior:**
- Analyzes the URI under the cursor
- Determines the appropriate action based on URI type
- Opens local files in Vim or external applications via OS

### Supported URI Types

#### Local Files
```markdown
[Document](./document.md)
[Document with line number](./document.md:42)
[Document with anchor](./document.md#section-title)
```

#### Web URLs
```markdown
[Google](https://www.google.com)
[Example](http://example.com)
```

#### Reference Links
```markdown
[Link text][reference]

[reference]: https://example.com
```

#### Internal Links
```markdown
[Section](#section-title)
[Another Section](#another-section)
```

#### Environment Variables
```markdown
[$HOME/documents](file:///home/user/documents)
[$VIMWIKI_PATH/notes.md](file:///path/to/vimwiki/notes.md)
```

## Python API

### Core Modules

#### `vimania_uri_.mdnav`

**`parse_line(line, cursor_pos)`**
Parses a line of text to extract URI information at the cursor position.

```python
from vimania_uri_.mdnav import parse_line

# Parse markdown link
result = parse_line("[Example](https://example.com)", 10)
# Returns: URI information dictionary
```

**Parameters:**
- `line` (str): The line of text to parse
- `cursor_pos` (int): Current cursor position in the line

**Returns:**
- `str | None`: Extracted URI or None if no valid URI found

**`open_uri(uri, extensions=None)`**
Opens a URI using the appropriate method.

```python
from vimania_uri_.mdnav import open_uri

# Open a local file
open_uri("./document.md", extensions=['.md', '.txt'])

# Open a web URL
open_uri("https://example.com")
```

**Parameters:**
- `uri` (str): The URI to open
- `extensions` (list, optional): File extensions to open in Vim

**Returns:**
- `dict`: Result dictionary with success status and metadata

#### `vimania_uri_.vim_.vimania_manager`

**`VimaniaUriManager`**
Main manager class for URI handling operations.

```python
from vimania_uri_.vim_.vimania_manager import VimaniaUriManager

manager = VimaniaUriManager()
result = manager.handle_uri(uri="https://example.com")
```

**Methods:**

**`handle_uri(uri, cursor_pos=None, line=None)`**
- `uri` (str): URI to handle
- `cursor_pos` (int, optional): Cursor position
- `line` (str, optional): Full line context
- Returns: Processing result dictionary

**`get_url_title(url)`**
Fetches the title of a web page (delegates to Rust).

- `url` (str): URL to fetch title from
- Returns: Page title string or error message


## Rust API

### Core Functions

The Rust API is exposed through PyO3 bindings in the `vimania_uri_rs` module.

#### `get_url_title(url: str) -> str`
Fetches the title of a web page with high performance.

```python
import vimania_uri_rs

title = vimania_uri_rs.get_url_title("https://www.rust-lang.org/")
# Returns: "Rust Programming Language"
```

**Features:**
- HTTP/HTTPS support only (security)
- SSRF protection (blocks internal networks)
- 3-second timeout
- User-agent string: `vimania-uri-rs/1.1.7`
- HTML title extraction with fallback handling

**Error Handling:**
- Raises `RuntimeError` for network failures
- Raises `RuntimeError` for invalid URLs
- Raises `RuntimeError` for security violations

#### `reverse_line(line: str) -> str`
Simple test function for PyO3 binding verification.

```python
import vimania_uri_rs

reversed_text = vimania_uri_rs.reverse_line("hello")
# Returns: "olleh"
```

### Security Features

#### URL Validation
The Rust core implements comprehensive URL validation:

- **Scheme Restriction**: Only HTTP and HTTPS allowed
- **SSRF Protection**: Blocks access to:
  - `localhost`, `127.0.0.1`, `::1`
  - Private networks: `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`
- **Timeout Protection**: 3-second connection and request timeouts

#### Custom Error Types
```rust
pub enum UriError {
    InvalidUrl(url::ParseError),
    HttpError(reqwest::Error),
    HtmlError(String),
    UnsupportedScheme(String),
    ForbiddenHost(String),
}
```

## Configuration Reference

### Global Variables

#### `g:vimania_uri_extensions`
**Type:** List of strings  
**Default:** `['.md', '.txt', '.rst', '.py', '.conf', '.sh', '.json', '.yaml', '.yml']`  
**Description:** File extensions that should be opened in Vim rather than external applications.

```vim
let g:vimania_uri_extensions = ['.md', '.txt', '.py']
```


#### `g:vimania_uri_log_level`
**Type:** String  
**Default:** `'INFO'`  
**Options:** `'DEBUG'`, `'INFO'`, `'WARNING'`, `'ERROR'`  
**Description:** Controls logging verbosity.

```vim
let g:vimania_uri_log_level = 'DEBUG'
```

#### `g:vimania_uri_timeout`
**Type:** Integer  
**Default:** `3000`  
**Description:** HTTP request timeout in milliseconds.

```vim
let g:vimania_uri_timeout = 5000
```

#### `g:vimania_uri_browser_cmd`
**Type:** String  
**Default:** System default  
**Description:** Custom browser command for web URLs.

```vim
let g:vimania_uri_browser_cmd = 'firefox'
```

### Environment Variables

#### `BKMR_DB_URL`
**Description:** Database connection string for bkmr integration.  
**Example:** `sqlite:///home/user/.config/bkmr/bkmr.db`

#### `LOG_LEVEL`
**Description:** Override plugin log level.  
**Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`

#### `VIMANIA_URI_TIMEOUT`
**Description:** HTTP timeout in seconds (overrides Vim setting).  
**Example:** `5`

## Integration Hooks

### Custom URI Handlers

You can extend the plugin with custom URI handlers:

```vim
function! CustomProtocolHandler(uri)
    if a:uri =~# '^custom://'
        " Handle custom protocol
        echo "Handling custom URI: " . a:uri
        return 1
    endif
    return 0
endfunction

" Register custom handler
autocmd User VimaniaUriPre call CustomProtocolHandler(expand('<cWORD>'))
```


### Pre/Post Processing Hooks

```vim
" Pre-processing hook
function! VimaniaUriPre()
    " Called before URI processing
    echo "Processing URI..."
endfunction

" Post-processing hook  
function! VimaniaUriPost()
    " Called after URI processing
    echo "URI processed!"
endfunction

autocmd User VimaniaUriPre call VimaniaUriPre()
autocmd User VimaniaUriPost call VimaniaUriPost()
```

## Error Handling

### Python Exceptions

#### `VimaniaUriError`
Base exception class for plugin errors.

```python
class VimaniaUriError(Exception):
    """Base exception for vimania-uri-rs errors"""
    pass
```

#### `InvalidUriError`
Raised when a URI cannot be parsed or is invalid.

```python
class InvalidUriError(VimaniaUriError):
    """Raised for invalid URI formats"""
    pass
```

#### `SecurityError`
Raised when a URI violates security policies.

```python
class SecurityError(VimaniaUriError):
    """Raised for security policy violations"""
    pass
```

### Rust Error Mapping

Rust errors are automatically converted to Python exceptions:

```python
try:
    title = vimania_uri_rs.get_url_title("http://localhost/test")
except RuntimeError as e:
    if "ForbiddenHost" in str(e):
        print("Access to local network blocked for security")
    elif "InvalidUrl" in str(e):
        print("Invalid URL format")
    elif "HttpError" in str(e):
        print("Network request failed")
```

### Logging

The plugin uses Python's logging module with configurable levels:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger names
logger = logging.getLogger('vimania_uri')
```

### Debugging

Enable verbose debugging:

```vim
" In Vim
let g:vimania_uri_log_level = 'DEBUG'

" Or set environment variable
let $LOG_LEVEL = 'DEBUG'
```

```bash
# In shell
export LOG_LEVEL=DEBUG
vim
```

For Python debugging:

```python
import vimania_uri_rs
print(vimania_uri_rs.__doc__)  # Module documentation
print(dir(vimania_uri_rs))     # Available functions
```

## Performance Considerations

### Rust Core Benefits
- **10x faster startup**: Rust module loads significantly faster than pure Python
- **Efficient HTTP requests**: Reused HTTP client with connection pooling
- **Memory efficiency**: Lower memory footprint for HTML parsing
- **Concurrent safety**: Thread-safe operations with proper error handling

### Optimization Tips
1. Keep `g:vimania_uri_extensions` list minimal for faster file type detection
2. Use environment variables for configuration to avoid Vim startup overhead
3. Enable bkmr integration only when needed
4. Set appropriate timeout values for your network conditions

### Benchmarks
- **URL title fetching**: ~50ms average (vs ~500ms pure Python)
- **Plugin initialization**: ~5ms (vs ~50ms pure Python)
- **Large file navigation**: ~2ms (vs ~20ms pure Python)

---

*For more examples and advanced usage, see the [DEVELOPMENT.md](../DEVELOPMENT.md) guide.*