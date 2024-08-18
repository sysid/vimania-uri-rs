use anyhow::{Context, Result};
use log::{debug, info, error, LevelFilter};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3_log::{Caching, Logger};
use reqwest::Url;
use scraper::{Html, Selector};
use stdext::function_name;

use core::time::Duration;

#[pyfunction]
fn reverse_line(line: String) -> PyResult<String> {
    Ok(line.chars().rev().collect())
}

#[pyfunction]
fn get_url_title(py: Python, url: &str) -> PyResult<String> {
    // Ok(String::from("Dummy Title")) // Simplified for testing
    debug!("({}:{}) {:?}", function_name!(), line!(), url);
    let title = py.allow_threads(|| {
        /* same code as before */
        _get_url_title(url).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get URL title: {}", e))
        })
    });
    info!("({}:{}) {:?}", function_name!(), line!(), title);
    title
}

fn _get_url_title(url: &str) -> Result<String> {
    // println!("Fetching URL title for: {}", url);
    // Ok(String::from("Dummy Title")) // Simplified for testing

    // Validate the URL
    let url = Url::parse(url).context("Failed to parse URL")?;

    // Create an HTTP client
    let client = reqwest::blocking::Client::builder()
        .connect_timeout(Duration::from_secs(3))
        .timeout(Duration::from_secs(3))
        .build()
        .unwrap();

    // Fetch the page
    info!("Fetching URL title for: {}", url);
    let res = client.get(url).send().context("Failed to send HTTP request")?;

    let body = res.text().context("Failed to read response body")?;

    // Parse the HTML
    let document = Html::parse_document(&body);
    let selector = Selector::parse("title")
        .map_err(|e| anyhow::anyhow!("Failed to parse selector: {:?}", e))?; // Manually converting the error

    let title = document
        .select(&selector)
        .next()
        .ok_or_else(|| anyhow::anyhow!("No title element found"))?
        .inner_html()
        .trim()
        .to_string();

    Ok(title)
}

#[pymodule]
fn vimania_uri_rs(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // let handle = pyo3_log::init();
    // configure logger so that certain creates have diffrent log levels

    let log_handle = Logger::new(py, Caching::LoggersAndLevels)?
        .filter(LevelFilter::Trace)
        // .filter_target("my_module::verbose_submodule".to_owned(), LevelFilter::Warn)
        // .filter_target("vimania_uri_rs".to_owned(), LevelFilter::Debug) // Ensure your crate is set to debug
        .filter_target("html5ever".to_owned(), LevelFilter::Warn)
        .filter_target("selectors".to_owned(), LevelFilter::Warn)
        .filter_target("build_wheels".to_owned(), LevelFilter::Warn)
        .filter_target("filelock".to_owned(), LevelFilter::Warn)
        .install()
        .expect("Someone installed a logger before us :-(");

    // log::logger().flush();
    println!("Log level: {}", log::max_level());

    info!("xxxxxxxx Debug mode: info");
    error!("xxxxxxx Debug mode: error");
    m.add_function(wrap_pyfunction!(reverse_line, m)?)?;
    m.add_function(wrap_pyfunction!(get_url_title, m)?)?;
    Ok(())
}

// test for _get_url_title
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test__get_url_title() {
        let url = "https://www.rust-lang.org/";
        let title = _get_url_title(url).unwrap();
        assert_eq!(title, "Rust Programming Language");
    }

    // #[test]
    // fn test_get_url_title() {
    //     let url = "https://www.rust-lang.org/";
    //     let title = get_url_title(url).unwrap();
    //     assert_eq!(title, "Rust Programming Language");
    // }
}