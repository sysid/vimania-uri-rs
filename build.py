import glob
import subprocess
import sys
import os
import platform
import argparse
from typing import List


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build and install the Rust extension with optional development mode.")
    parser.add_argument(
        "-d", "--dev",
        action="store_true",
        help="Build and install the development version (debug mode)."
    )
    return parser.parse_args()


def ensure_cargo_installed() -> None:
    """Ensure that Cargo (Rust's package manager) is installed."""
    try:
        subprocess.run(["cargo", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Cargo (Rust) is not installed.")
        sys.exit(1)
    except FileNotFoundError:
        print("Cargo (Rust) is not installed.")
        sys.exit(1)


def build_rust_extension(python_executable: str, is_dev: bool) -> None:
    """Build the Rust extension using maturin."""
    print(f"Building Rust extension in {'release' if not is_dev else 'development'} mode.")

    try:
        if is_dev:
            subprocess.run([
                "maturin", "build",
                "--bindings", "pyo3",
                "--interpreter", python_executable,
            ], check=True)
        else:
            subprocess.run([
                "maturin", "build",
                "--release",
                "--bindings", "pyo3",
                "--interpreter", python_executable,
            ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to build the Rust extension: {e}")
        sys.exit(1)



def find_wheel_file(wheels_dir: str) -> str:
    """Locate the generated wheel file for the current Python version."""
    python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
    wheel_files = glob.glob(os.path.join(wheels_dir, f"*{python_version}*.whl"))

    if not wheel_files:
        print(f"No wheel file found for Python {python_version}.")
        all_wheels = glob.glob(os.path.join(wheels_dir, "*.whl"))
        if all_wheels:
            print("Available wheels:", "\n".join(all_wheels))
        sys.exit(1)

    # If multiple files exist, take the most recent one
    return sorted(wheel_files)[-1]

def install_wheel(wheel_file: str, target_dir: str, python_executable: str) -> None:
    """Install the wheel file into the specified target directory."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    try:
        subprocess.run([
            python_executable, "-m", "pip", "install",
            "--target", target_dir,
            "--force-reinstall",  # Ensure the wheel is installed even if it's already present
            "--upgrade",
            wheel_file,
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install the wheel file into the {target_dir} directory: {e}")
        sys.exit(1)

    print(f"Successfully installed {wheel_file} into {target_dir}")


def install_python_dependencies(requirements_file: str, target_dir: str, python_executable: str) -> None:
    """Install Python dependencies listed in the requirements.txt file into the target directory."""
    if os.path.exists(requirements_file):
        print(f"Installing dependencies from {requirements_file} into {target_dir}")

        try:
            subprocess.run([
                python_executable, "-m", "pip", "install",
                "--target", target_dir,
                "-r", requirements_file,
                "--force-reinstall",  # Ensure the wheel is installed even if it's already present
                "--upgrade",
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies from {requirements_file}: {e}")
            sys.exit(1)
    else:
        print(f"No requirements.txt found at {requirements_file}. Skipping dependency installation.")


def build_and_install_extension(is_dev: bool) -> None:
    """Main function to build the Rust extension and install it, along with any Python dependencies."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    target_os = platform.system().lower()
    python_path = sys.executable

    print(f"Building Rust extension for Python {python_version} on {target_os}: {python_path}")

    ensure_cargo_installed()
    build_rust_extension(python_path, is_dev)

    wheels_dir = os.path.join("target", "wheels")
    wheel_file = find_wheel_file(wheels_dir)
    print(f"Found wheel file: {wheel_file}")

    pythonx_dir = os.path.join(os.path.dirname(__file__), "pythonx")
    install_wheel(wheel_file, pythonx_dir, python_path)

    # Install dependencies from requirements.txt
    requirements_file = os.path.join(pythonx_dir, "requirements.txt")
    install_python_dependencies(requirements_file, pythonx_dir, python_path)


if __name__ == "__main__":
    args = parse_arguments()
    build_and_install_extension(args.dev)
