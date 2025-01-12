#!/usr/bin/env python3
import yaml
import os
from pathlib import Path

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
    models_dir = os.path.join(src_dir, "models")
    tests_dir = os.path.join(base_dir, "tests")

    # Create directories
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(api_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Create __init__.py
    with open(os.path.join(src_dir, "__init__.py"), "w") as f:
        f.write(f'"""{app_name} FastAPI application package."""\n')

    # Write files using templates
    files_to_generate = {
        "main.py": ("main_content.py", src_dir),
        f"{app_name}_api.py": ("api_content.py", api_dir),
        "README.md": ("README.md", base_dir),
        "pyproject.toml": ("pyproject_content.toml", base_dir),
        f"test_{app_name}.py": ("test_file_content.py", tests_dir),
        f"{app_name}.py": ("model_content.py", models_dir),
    }

    for output_filename, (template_filename, target_dir) in files_to_generate.items():
        file_content = load_template(template_filename, app_name)
        with open(os.path.join(target_dir, output_filename), "w") as f:
            f.write(file_content)

    print(f"✅ FastAPI application '{app_name}' created successfully at {base_dir}")


# Define type mappings from YAML to Python/Pydantic
TYPE_MAP = {
    "int": "int",
    "string": "str",
    "list[string]": "list[str]",
    "list[int]": "list[int]",
}


def parse_type(field_type):
    """Convert YAML types to Python/Pydantic types."""
    if field_type in TYPE_MAP:
        return TYPE_MAP[field_type]
    elif field_type.startswith("list["):
        inner_type = field_type[5:-1]
        return f"list[{parse_type(inner_type)}]"
    return field_type  # Assume it's another model reference


def generate_pydantic_model(name, fields):
    """Generate a Pydantic model definition."""
    model_str = f"from pydantic import BaseModel\nfrom typing import List, Optional\n\n"
    model_str += f"class {name.capitalize()}(BaseModel):\n"

    for field_name, field_type in fields.items():
        python_type = parse_type(field_type)
        model_str += f"    {field_name}: {python_type}\n"

    return model_str


def main(app_name:str):
    # Load YAML
    with open(f"apps/{app_name}.yml", "r") as file:
        data = yaml.safe_load(file)

    # app_name = data["app"]["name"].lower()
    models = data["app"]["models"]

    # Define the app directory structure
    app_dir = Path(f"../apps/{app_name}")
    models_dir = app_dir / f"src/{app_name}/models"
    
    # Ensure directories exist
    models_dir.mkdir(parents=True, exist_ok=True)

    # Generate models
    for model_name, fields in models.items():
        model_code = generate_pydantic_model(model_name, fields)

        # Save model file
        model_file = models_dir / f"{model_name.lower()}.py"
        with open(model_file, "w") as f:
            f.write(model_code)

        print(f"Generated: {model_file}")



if __name__ == "__main__":
    app_name = input("Enter the FastAPI application name: ").strip()
    monorepo_root = input("Enter the monorepo root directory (e.g., ~/projects/python-monorepo): ").strip()
    main(app_name)
    create_fastapi_application(app_name, os.path.expanduser(monorepo_root))
