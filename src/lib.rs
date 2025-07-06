//! # Vimania URI Rust
//!
//! High-performance URI handling for Vim with Python bindings.
//!
//! This module provides fast URL title fetching and validation
//! with security features to prevent SSRF attacks.

use anyhow::Result;
use log::{debug, info, LevelFilter};
use once_cell::sync::Lazy;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3_log::{Caching, Logger};
use reqwest::blocking::Client;
use scraper::{Html, Selector};
use stdext::function_name;
use thiserror::Error;
use url::Url;

use core::time::Duration;

/// Custom error types for URI handling
#[derive(Debug, Error)]
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

/// Static HTTP client with optimal configuration
static HTTP_CLIENT: Lazy<Client> = Lazy::new(|| {
    reqwest::blocking::Client::builder()
        .connect_timeout(Duration::from_secs(3))
        .timeout(Duration::from_secs(3))
        .user_agent("vimania-uri-rs/1.1.7")
        .build()
        .expect("Failed to create HTTP client")
});

/// Validate URL to prevent SSRF attacks and ensure safe access
fn validate_url(url_str: &str) -> Result<Url, UriError> {
    let url = Url::parse(url_str)?;

    // Only allow HTTP and HTTPS schemes
    match url.scheme() {
        "http" | "https" => {}
        scheme => return Err(UriError::UnsupportedScheme(scheme.to_string())),
    }

    // Prevent access to local/internal networks
    if let Some(host) = url.host_str() {
        if host == "localhost"
            || host == "127.0.0.1"
            || host == "::1"
            || host.starts_with("192.168.")
            || host.starts_with("10.")
            || host.starts_with("172.16.")
            || host.starts_with("172.17.")
            || host.starts_with("172.18.")
            || host.starts_with("172.19.")
            || host.starts_with("172.20.")
            || host.starts_with("172.21.")
            || host.starts_with("172.22.")
            || host.starts_with("172.23.")
            || host.starts_with("172.24.")
            || host.starts_with("172.25.")
            || host.starts_with("172.26.")
            || host.starts_with("172.27.")
            || host.starts_with("172.28.")
            || host.starts_with("172.29.")
            || host.starts_with("172.30.")
            || host.starts_with("172.31.")
        {
            return Err(UriError::ForbiddenHost(host.to_string()));
        }
    }

    Ok(url)
}

/// Simple test function to reverse a line (for testing PyO3 bindings)
#[pyfunction]
fn reverse_line(line: String) -> PyResult<String> {
    Ok(line.chars().rev().collect())
}

/// Get the title of a web page (Python binding)
///
/// This function provides a Python interface to the URL title fetching functionality.
/// It includes proper error handling and logging.
#[pyfunction]
fn get_url_title(py: Python, url: &str) -> PyResult<String> {
    debug!("({}:{}) {:?}", function_name!(), line!(), url);
    let title = py.allow_threads(|| {
        _get_url_title(url).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get URL title: {}", e))
        })
    });
    info!("({}:{}) {:?}", function_name!(), line!(), title);
    title
}

/// Fetch the title of a web page from the given URL
///
/// # Arguments
/// * `url` - A string slice containing the URL to fetch
///
/// # Returns
/// * `Result<String, UriError>` - The title of the page or an error
///
/// # Examples
/// ```
/// let title = _get_url_title("https://example.com")?;
/// ```
///
/// # Errors
/// This function will return an error if:
/// - The URL is malformed
/// - The URL scheme is not HTTP/HTTPS
/// - The URL points to a local/internal network
/// - The HTTP request fails
/// - The HTML cannot be parsed
/// - No title element is found
fn _get_url_title(url: &str) -> Result<String, UriError> {
    // Validate and sanitize the URL
    let url = validate_url(url)?;

    // Use the static HTTP client for better performance
    info!("Fetching URL title for: {}", url);
    let res = HTTP_CLIENT.get(url).send()?;

    let body = res.text()?;

    // Parse the HTML
    let document = Html::parse_document(&body);
    let selector = Selector::parse("title")
        .map_err(|e| UriError::HtmlError(format!("Failed to parse title selector: {:?}", e)))?;

    let title = document
        .select(&selector)
        .next()
        .ok_or_else(|| UriError::HtmlError("No title element found".to_string()))?
        .inner_html()
        .trim()
        .to_string();

    // todo: check whether this can be activeted
    // Ensure title is not empty
    //if title.is_empty() {
    //    return Err(UriError::HtmlError("Title element is empty".to_string()));
    //}

    Ok(title)
}

#[pymodule]
fn vimania_uri_rs(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // let handle = pyo3_log::init();
    // configure logger so that certain creates have diffrent log levels
    let _ = Logger::new(py, Caching::LoggersAndLevels)?
        .filter(LevelFilter::Trace)
        // .filter_target("my_module::verbose_submodule".to_owned(), LevelFilter::Warn)
        .filter_target("html5ever".to_owned(), LevelFilter::Warn)
        .filter_target("selectors".to_owned(), LevelFilter::Warn)
        .filter_target("build_wheels".to_owned(), LevelFilter::Warn)
        .filter_target("filelock".to_owned(), LevelFilter::Warn)
        .install()
        .expect("Someone installed a logger before us :-(");

    info!("Log level: {}", log::max_level());
    m.add_function(wrap_pyfunction!(reverse_line, m)?)?;
    m.add_function(wrap_pyfunction!(get_url_title, m)?)?;
    Ok(())
}

// test for _get_url_title
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_url_title() {
        let url = "https://www.rust-lang.org/";
        let title = _get_url_title(url).unwrap();
        assert_eq!(title, "Rust Programming Language");
    }

    #[test]
    fn test_validate_url_security() {
        // Valid URLs should pass
        assert!(validate_url("https://www.google.com").is_ok());
        assert!(validate_url("http://example.com").is_ok());

        // Invalid schemes should fail
        assert!(matches!(
            validate_url("ftp://example.com"),
            Err(UriError::UnsupportedScheme(_))
        ));
        assert!(matches!(
            validate_url("file:///etc/passwd"),
            Err(UriError::UnsupportedScheme(_))
        ));

        // Local/internal networks should fail
        assert!(matches!(
            validate_url("http://localhost"),
            Err(UriError::ForbiddenHost(_))
        ));
        assert!(matches!(
            validate_url("http://127.0.0.1"),
            Err(UriError::ForbiddenHost(_))
        ));
        assert!(matches!(
            validate_url("http://192.168.1.1"),
            Err(UriError::ForbiddenHost(_))
        ));
        assert!(matches!(
            validate_url("http://10.0.0.1"),
            Err(UriError::ForbiddenHost(_))
        ));
        assert!(matches!(
            validate_url("http://172.16.0.1"),
            Err(UriError::ForbiddenHost(_))
        ));
    }
}
