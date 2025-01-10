#!/usr/bin/env python3

import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "tpl")

def load_template(template_file: str, app_name: str) -> str:
    """Loads a template file and replaces placeholders with the application name."""
    template_path = os.path.join(TEMPLATE_DIR, template_file)
    with open(template_path, "r") as f:
        content = f.read()
    return content.replace("{app_name}", app_name).replace("{AppName}", app_name.capitalize())

def create_fastapi_application(app_name: str, monorepo_root: str):
    """
    Creates a structured FastAPI application directory inside the monorepo.
    """

    # Define base paths
    base_dir = os.path.join(monorepo_root, "apps", app_name)
    src_dir = os.path.join(base_dir, "src", app_name)
    api_dir = os.path.join(src_dir, "api")
    tests_dir = os.path.join(base_dir, "tests")

    # Create directories
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(api_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Create __init__.py
    with open(os.path.join(src_dir, "__init__.py"), "w") as f:
        f.write(f'"""{app_name} FastAPI application package."""\n')

    # Write files using templates
    files_to_generate = {
        "main.py": ("main_content.py", src_dir),
        f"{app_name}.py": ("api_content.py", api_dir),
        "README.md": ("README.md", base_dir),
        "pyproject.toml": ("pyproject_content.toml", base_dir),
        f"test_{app_name}.py": ("test_file_content.py", tests_dir),
    }

    for output_filename, (template_filename, target_dir) in files_to_generate.items():
        file_content = load_template(template_filename, app_name)
        with open(os.path.join(target_dir, output_filename), "w") as f:
            f.write(file_content)

    print(f"✅ FastAPI application '{app_name}' created successfully at {base_dir}")

if __name__ == "__main__":
    app_name = input("Enter the FastAPI application name: ").strip()
    monorepo_root = input("Enter the monorepo root directory (e.g., ~/projects/python-monorepo): ").strip()
    create_fastapi_application(app_name, os.path.expanduser(monorepo_root))
