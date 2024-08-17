use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use reqwest::blocking::Client;
use reqwest::Url;
use scraper::{Html, Selector};

#[pyfunction]
fn reverse_line(line: String) -> PyResult<String> {
    Ok(line.chars().rev().collect())
}

#[pyfunction]
fn get_url_title(url: &str) -> PyResult<String> {
    // println!("Fetching URL title for: {}", url);
    // Ok(String::from("Dummy Title")) // Simplified for testing

    // Validate the URL
    let url = Url::parse(url).map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid URL"))?;

    // Create an HTTP client
    let client = Client::new();

    // Fetch the page
    let res = client.get(url).send().map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to fetch URL: {}", e))
    })?;

    let body = res.text().map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to read response body: {}", e))
    })?;

    // Parse the HTML
    let document = Html::parse_document(&body);
    let selector = Selector::parse("title").map_err(|_| {
        pyo3::exceptions::PyRuntimeError::new_err("Failed to parse HTML selector")
    })?;
    let title = document
        .select(&selector)
        .next()
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("No title element found"))?
        .inner_html()
        .trim()
        .to_string();

    Ok(title)
}

#[pymodule]
fn vimania_uri_rs(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(reverse_line, m)?)?;
    m.add_function(wrap_pyfunction!(get_url_title, m)?)?;
    Ok(())
}