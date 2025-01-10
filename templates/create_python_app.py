import os

def create_python_app(app_name: str, monorepo_root: str):
    """Creates a structured Python application directory inside the monorepo."""
    
    # Define base paths
    base_dir = os.path.join(monorepo_root, "apps", app_name)
    src_dir = os.path.join(base_dir, "src", app_name)
    tests_dir = os.path.join(base_dir, "tests")
    scripts_dir = os.path.join(base_dir, "scripts")

    # Create directories
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    # Create __init__.py inside the package
    with open(os.path.join(src_dir, "__init__.py"), "w") as f:
        f.write(f'"""{app_name} application package."""\n')

    # Create main.py (Application entry point)
    main_content = f"""\
import sys

def main():
    print("Welcome to {app_name}!")

if __name__ == "__main__":
    main()
"""
    with open(os.path.join(src_dir, "main.py"), "w") as f:
        f.write(main_content)

    # Create README.md
    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write(f"# {app_name}\n\nThis is the `{app_name}` Python application.\n")

    # Create LICENSE
    with open(os.path.join(base_dir, "LICENSE"), "w") as f:
        f.write("MIT License\n")

    # Create pyproject.toml
    pyproject_content = f"""\
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{app_name}"
version = "0.1.0"
description = "A Python application in a monorepo"
authors = [{{ name = "Your Name", email = "your@email.com" }}]
dependencies = [
    "fastapi",
    "uvicorn",
    "requests",
    "pydantic"
]

[project.optional-dependencies]
dev = ["pytest"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
    with open(os.path.join(base_dir, "pyproject.toml"), "w") as f:
        f.write(pyproject_content)

    # Create .env file for environment variables
    with open(os.path.join(base_dir, ".env"), "w") as f:
        f.write("# Environment variables for the application\n")

    # Create a sample test file
    test_file_content = f"""\
import pytest
from {app_name}.main import main

def test_main_output(capsys):
    main()
    captured = capsys.readouterr()
    assert "Welcome to {app_name}!" in captured.out
"""
    with open(os.path.join(tests_dir, f"test_{app_name}.py"), "w") as f:
        f.write(test_file_content)

    # Create start.sh script
    start_script_content = f"""\
#!/bin/bash
echo "Starting {app_name}..."
python -m {app_name}.main
"""
    with open(os.path.join(scripts_dir, "start.sh"), "w") as f:
        f.write(start_script_content)

    # Make the script executable
    os.chmod(os.path.join(scripts_dir, "start.sh"), 0o755)

    print(f"✅ Application '{app_name}' created successfully at {base_dir}")

# Get user input
app_name = input("Enter the application name: ").strip()
monorepo_root = input("Enter the monorepo root directory (e.g., ~/projects/python-monorepo): ").strip()
create_python_app(app_name, os.path.expanduser(monorepo_root))
