#!/usr/bin/env python3
import yaml
import os
from pathlib import Path

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "tpl")


def load_template(template_file: str, app_name: str, model_name: str, model_name_cap: str) -> str:
    """Loads a template file and replaces placeholders with the application and model names."""
    template_path = os.path.join(TEMPLATE_DIR, template_file)
    with open(template_path, "r") as f:
        content = f.read()
    
    return (content
            .replace("{app_name}", app_name)
            .replace("{model_name}", model_name)
            .replace("{ModelName}", model_name_cap))


def create_fastapi_application(app_name: str, monorepo_root: str, models: dict):
    """
    Creates a structured FastAPI application directory inside the monorepo.
    Now it generates `{model_name}_api.py` for each model using the provided template.
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

    # Create __init__.py files
    for directory in [src_dir, api_dir, models_dir]:
        with open(os.path.join(directory, "__init__.py"), "w") as f:
            f.write(f'"""{app_name} package."""\n')

    # Generate main.py
    main_content = f"""from fastapi import FastAPI

app = FastAPI()

# Import and include routers
"""
    for model_name in models.keys():
        main_content += f"from .api.{model_name.lower()}_api import router as {model_name.lower()}_router\n"
        main_content += f"app.include_router({model_name.lower()}_router, prefix='/{model_name.lower()}')\n"

    main_file = os.path.join(src_dir, "main.py")
    with open(main_file, "w") as f:
        f.write(main_content)

    print(f"✅ Created FastAPI app structure at {base_dir}")


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


def main(app_name: str, monorepo_root: str):
    # Load YAML
    yaml_path = f"apps/{app_name}.yml"
    with open(yaml_path, "r") as file:
        data = yaml.safe_load(file)

    models = data["app"]["models"]

    # Define the app directory structure
    app_dir = Path(monorepo_root) / "apps" / app_name
    models_dir = app_dir / f"src/{app_name}/models"
    api_dir = app_dir / f"src/{app_name}/api"

    # Ensure directories exist
    models_dir.mkdir(parents=True, exist_ok=True)
    api_dir.mkdir(parents=True, exist_ok=True)

    # Generate Pydantic models and API routes
    for model_name, fields in models.items():
        model_code = generate_pydantic_model(model_name, fields)
        api_code = load_template("api_content.py", app_name, model_name, model_name.capitalize())

        # Save model file
        model_file = models_dir / f"{model_name.lower()}.py"
        with open(model_file, "w") as f:
            f.write(model_code)

        # Save API file
        api_file = api_dir / f"{model_name.lower()}_api.py"
        with open(api_file, "w") as f:
            f.write(api_code)

        print(f"✅ Generated model: {model_file}")
        print(f"✅ Generated API: {api_file}")

    # Generate FastAPI application structure
    create_fastapi_application(app_name, monorepo_root, models)

    print(f"✅ FastAPI application '{app_name}' setup completed!")


if __name__ == "__main__":
    app_name = input("Enter the FastAPI application name: ").strip()
    monorepo_root = input("Enter the monorepo root directory (e.g., ~/projects/python-monorepo): ").strip()
    monorepo_root = os.path.expanduser(monorepo_root)

    main(app_name, monorepo_root)
