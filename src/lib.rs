use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

/// Reverses the content of the current line in the Vim buffer.
#[pyfunction]
fn reverse_line(line: String) -> PyResult<String> {
    Ok(line.chars().rev().collect())
}

/// This module is a Python module implemented in Rust.
// #[pymodule]
// fn vimania_uri_rs(py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(reverse_line, m)?)?;
//     Ok(())
// }

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn vimania_uri_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(reverse_line, m)?)
}