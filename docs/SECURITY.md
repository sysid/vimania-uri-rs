# Security Documentation

This document outlines the security features, considerations, and best practices for vimania-uri-rs.

## Table of Contents

- [Security Architecture](#security-architecture)
- [SSRF Protection](#ssrf-protection)
- [Input Validation](#input-validation)
- [Network Security](#network-security)
- [Dependency Security](#dependency-security)
- [Best Practices](#best-practices)
- [Reporting Security Issues](#reporting-security-issues)

## Security Architecture

### Defense in Depth

vimania-uri-rs implements multiple layers of security:

1. **Input Validation**: Strict URL parsing and validation
2. **Network Restrictions**: SSRF protection and timeout controls
3. **Dependency Management**: Regular security audits and updates
4. **Secure Defaults**: Conservative configuration out of the box

### Threat Model

**Protected Against:**
- ✅ Server-Side Request Forgery (SSRF) attacks
- ✅ Malicious URL schemes (file://, ftp://, etc.)
- ✅ Access to internal/private networks
- ✅ Infinite HTTP requests (timeout protection)
- ✅ Malicious HTML/JavaScript execution
- ✅ Dependency vulnerabilities

**Not Protected Against:**
- ❌ Malicious content in fetched pages (user responsibility)
- ❌ DNS spoofing (relies on system DNS)
- ❌ Social engineering attacks
- ❌ Vim/OS-level vulnerabilities

## SSRF Protection

### Blocked Network Ranges

The plugin automatically blocks requests to:

```rust
// Localhost variants
"localhost", "127.0.0.1", "::1"

// Private IPv4 ranges (RFC 1918)
"192.168.0.0/16"    // 192.168.0.0 - 192.168.255.255
"10.0.0.0/8"        // 10.0.0.0 - 10.255.255.255
"172.16.0.0/12"     // 172.16.0.0 - 172.31.255.255

// Link-local addresses
"169.254.0.0/16"    // 169.254.0.0 - 169.254.255.255
```

### Implementation Details

```rust
fn validate_url(url_str: &str) -> Result<Url, UriError> {
    let url = Url::parse(url_str)?;

    // Only allow HTTP and HTTPS schemes
    match url.scheme() {
        "http" | "https" => {},
        scheme => return Err(UriError::UnsupportedScheme(scheme.to_string())),
    }

    // Prevent access to local/internal networks
    if let Some(host) = url.host_str() {
        if is_forbidden_host(host) {
            return Err(UriError::ForbiddenHost(host.to_string()));
        }
    }

    Ok(url)
}
```

### Testing SSRF Protection

```bash
# These should be blocked
curl -X POST http://localhost:8080/api/test \
  -d '{"url": "http://localhost:8080/admin"}'

curl -X POST http://localhost:8080/api/test \
  -d '{"url": "http://192.168.1.1/router"}'

curl -X POST http://localhost:8080/api/test \
  -d '{"url": "http://10.0.0.1/internal"}'
```

## Input Validation

### URL Parsing

All URLs undergo strict validation:

```rust
pub enum UriError {
    #[error("Invalid URL: {0}")]
    InvalidUrl(#[from] url::ParseError),
    #[error("HTTP request failed: {0}")]
    HttpError(#[from] reqwest::Error),
    #[error("HTML parsing failed: {0}")]
    HtmlError(String),
    #[error("Unsupported URL scheme: {0}")]
    UnsupportedScheme(String),
    #[error("Access to internal/local networks is not allowed: {0}")]
    ForbiddenHost(String),
}
```

### Sanitization

- **URL normalization**: URLs are parsed and normalized using the `url` crate
- **HTML parsing**: Safe HTML parsing with `scraper` crate (no JavaScript execution)
- **Path traversal protection**: Local file paths are resolved and validated

### Input Length Limits

```rust
const MAX_URL_LENGTH: usize = 2048;
const MAX_TITLE_LENGTH: usize = 1024;
const MAX_HTML_SIZE: usize = 1_048_576; // 1MB
```

## Network Security

### HTTP Client Configuration

```rust
static HTTP_CLIENT: Lazy<Client> = Lazy::new(|| {
    reqwest::blocking::Client::builder()
        .connect_timeout(Duration::from_secs(3))
        .timeout(Duration::from_secs(3))
        .user_agent("vimania-uri-rs/1.1.7")
        .redirect(reqwest::redirect::Policy::limited(3))
        .build()
        .expect("Failed to create HTTP client")
});
```

### Security Features

- **Connection timeout**: 3 seconds maximum
- **Request timeout**: 3 seconds maximum  
- **Redirect limits**: Maximum 3 redirects
- **User agent**: Clearly identifies the client
- **TLS verification**: Always enabled (no insecure connections)

### Network Monitoring

Monitor network requests in development:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Monitor with netstat
netstat -an | grep :80
netstat -an | grep :443
```

## Dependency Security

### Automated Security Scanning

The project uses multiple security scanning tools:

#### Rust Dependencies

```bash
# Install cargo-audit
cargo install cargo-audit

# Run security audit
cargo audit

# Check for outdated dependencies
cargo outdated
```

#### Python Dependencies

```bash
# Security scanning with bandit
uv run bandit -r pythonx/vimania_uri_rs

# Dependency vulnerability check
uv run pip-audit
```

### Dependency Policy

- **Rust dependencies**: Updated monthly, security issues addressed immediately
- **Python dependencies**: Pinned versions with regular security updates
- **Minimum supported versions**: Only maintained versions of dependencies

### Current Security Status

```bash
# Check current status
make security

# Example output:
# ✅ cargo audit: No vulnerabilities found
# ✅ bandit: No security issues found
# ✅ All dependencies up to date
```

## Best Practices

### For Users

1. **Keep Updated**: Regularly update the plugin
   ```bash
   pip install vimania-uri-rs --upgrade
   ```

2. **Review URLs**: Be cautious with unknown URLs
   ```vim
   " Preview URL before opening
   echo expand('<cWORD>')
   ```

3. **Configure Safely**: Use minimal necessary permissions
   ```vim
   let g:vimania_uri_extensions = ['.md', '.txt']  " Minimal list
   let g:vimania_uri_twbm_integration = 0         " Disable if not needed
   ```

4. **Monitor Logs**: Enable logging for security monitoring
   ```vim
   let g:vimania_uri_log_level = 'WARNING'
   ```

### For Developers

1. **Input Validation**: Always validate user input
   ```python
   def safe_url_handler(url):
       if not url or len(url) > MAX_URL_LENGTH:
           raise ValueError("Invalid URL length")
       
       # Use the Rust validation
       return vimania_uri_rs.get_url_title(url)
   ```

2. **Error Handling**: Handle security errors gracefully
   ```python
   try:
       title = vimania_uri_rs.get_url_title(url)
   except RuntimeError as e:
       if "ForbiddenHost" in str(e):
           log.warning(f"Blocked access to internal network: {url}")
           return "Access denied for security reasons"
       raise
   ```

3. **Testing**: Include security tests
   ```python
   def test_ssrf_protection():
       with pytest.raises(RuntimeError, match="ForbiddenHost"):
           vimania_uri_rs.get_url_title("http://localhost:8080")
   ```

### For System Administrators

1. **Network Policies**: Implement additional network restrictions
   ```bash
   # Example iptables rule to block outbound traffic to private ranges
   iptables -A OUTPUT -d 192.168.0.0/16 -j DROP
   iptables -A OUTPUT -d 10.0.0.0/8 -j DROP
   iptables -A OUTPUT -d 172.16.0.0/12 -j DROP
   ```

2. **Monitoring**: Monitor plugin usage
   ```bash
   # Monitor vim processes
   ps aux | grep vim
   
   # Monitor network connections
   netstat -tulpn | grep vim
   ```

3. **Sandboxing**: Consider running Vim in a sandbox
   ```bash
   # Example with firejail
   firejail --net=none vim document.md
   ```

## Security Configuration

### Secure Defaults

```vim
" Minimal attack surface configuration
let g:vimania_uri_extensions = ['.md', '.txt']
let g:vimania_uri_twbm_integration = 0
let g:vimania_uri_timeout = 3000
let g:vimania_uri_log_level = 'WARNING'
```

### High Security Environment

```vim
" For high-security environments
let g:vimania_uri_extensions = []  " Open nothing in Vim
let g:vimania_uri_twbm_integration = 0
let g:vimania_uri_timeout = 1000   " Shorter timeout
let g:vimania_uri_log_level = 'INFO'

" Disable web URL handling entirely
function! BlockWebUrls()
    if expand('<cWORD>') =~# '^https\?://'
        echo "Web URLs disabled in high-security mode"
        return
    endif
    " Only handle local files
    call vimania_uri#handle_local_only()
endfunction

nmap go :call BlockWebUrls()<CR>
```

### Environment Variables for Security

```bash
# Disable all network access
export VIMANIA_URI_NETWORK_DISABLED=1

# Custom timeout (lower for security)
export VIMANIA_URI_TIMEOUT=1

# Force HTTPS only
export VIMANIA_URI_HTTPS_ONLY=1
```

## Auditing and Compliance

### Security Audit Checklist

- [ ] All dependencies updated to latest secure versions
- [ ] SSRF protection tests passing
- [ ] No hardcoded credentials or secrets
- [ ] Input validation covering all entry points
- [ ] Error messages don't leak sensitive information
- [ ] Network timeouts properly configured
- [ ] TLS certificate validation enabled
- [ ] User agent string doesn't reveal sensitive info

### Compliance Considerations

#### GDPR/Privacy
- Plugin doesn't collect personal data
- URL requests are not logged by default
- No tracking or analytics

#### Corporate Environment
- No external dependencies at runtime (after installation)
- Configurable network restrictions
- Audit trail through logging
- No persistent storage of URLs

## Reporting Security Issues

### Responsible Disclosure

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security concerns to: [maintainer email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 24 hours
- **Initial assessment**: Within 72 hours  
- **Fix development**: Within 7 days for critical issues
- **Public disclosure**: After fix is released

### Hall of Fame

We acknowledge security researchers who help improve the project:

- [List of contributors who reported security issues]

## Security Testing

### Automated Tests

```bash
# Run security test suite
make security-test

# Individual security tests
cargo test security_
pytest tests/security/
```

### Manual Security Testing

```bash
# Test SSRF protection
python3 -c "
import vimania_uri_rs
try:
    vimania_uri_rs.get_url_title('http://localhost:22')
    print('FAIL: Should have blocked localhost')
except RuntimeError as e:
    print('PASS: Blocked localhost access')
"

# Test scheme validation
python3 -c "
import vimania_uri_rs
try:
    vimania_uri_rs.get_url_title('file:///etc/passwd')
    print('FAIL: Should have blocked file scheme')
except RuntimeError as e:
    print('PASS: Blocked file scheme')
"
```

### Penetration Testing

For organizations requiring penetration testing:

1. **Scope**: Focus on URL handling and network requests
2. **Test cases**: SSRF, injection, DoS, information disclosure
3. **Tools**: Custom scripts, burp suite, OWASP ZAP
4. **Documentation**: Provide test reports and remediation guidance

---

*This security documentation is updated with each release. Last updated: [Date]*