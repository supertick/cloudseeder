import os

def create_python_library(lib_name: str, location: str):
    """Creates a structured Python library directory inside the specified location."""
    
    # Define directory structure
    base_dir = os.path.join(location, "packages", lib_name)
    src_dir = os.path.join(base_dir, "src", lib_name)
    tests_dir = os.path.join(base_dir, "tests")
    
    # Create directories
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Create __init__.py inside package
    with open(os.path.join(src_dir, "__init__.py"), "w") as f:
        f.write(f'"""{lib_name} package."""\n')

    # Create README.md
    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write(f"# {lib_name}\n\nThis is the `{lib_name}` Python library.\n")

    # Create LICENSE
    with open(os.path.join(base_dir, "LICENSE"), "w") as f:
        f.write("MIT License\n")

    # Create pyproject.toml
    pyproject_content = f"""
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{lib_name}"
version = "0.1.0"
description = "A Python library for {lib_name}"
authors = [{{ name = "Your Name", email = "your@email.com" }}]
dependencies = []

[project.optional-dependencies]
dev = ["pytest"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
    with open(os.path.join(base_dir, "pyproject.toml"), "w") as f:
        f.write(pyproject_content.strip())

    # Create a sample test file
    test_file_content = f"""
import pytest
from {lib_name} import __version__

def test_version():
    assert __version__ == "0.1.0"
"""
    with open(os.path.join(tests_dir, f"test_{lib_name}.py"), "w") as f:
        f.write(test_file_content.strip())

    print(f"✅ Library '{lib_name}' created successfully at {base_dir}")

# Get user input
library_name = input("Enter the library name: ").strip()
location = input("Enter the root directory (e.g., ~/projects/python-monorepo): ").strip()
create_python_library(library_name, os.path.expanduser(location))
