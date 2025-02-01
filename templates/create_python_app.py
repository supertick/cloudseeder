#!/usr/bin/env python3
import argparse
import yaml
import os
from pathlib import Path

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "tpl")


def load_template(template_file: str, app_name: str = "", model_name: str = "", model_name_cap: str = "") -> str:
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
    api_routes = ""
    main_content = f"""from fastapi import FastAPI

app = FastAPI()

# Import and include routers
"""
    for model_name in models.keys():
        main_content += f"from .api.{model_name.lower()}_api import router as {model_name.lower()}_router\n"
        main_content += f"app.include_router({model_name.lower()}_router, prefix='/v1', tags=[\"{model_name.replace('_', ' ').title()}\"])\n"
        api_routes += f"from .api.{model_name.lower()}_api import router as {model_name.lower()}_router\n"
        api_routes += f"app.include_router({model_name.lower()}_router, prefix='/v1', tags=[\"{model_name.replace('_', ' ').title()}\"])\n"

    # main_file = os.path.join(src_dir, "main.py")
    # with open(main_file, "w") as f:
    #     f.write(main_content)

    replacements = {
        "{app_name}": app_name,
        "{APP_NAME}": app_name.upper(),
        "{AppName}": app_name.capitalize(),
        "{App Name}": app_name.replace("_", " ").title(),
        "{AppTitle}": app_name.replace("_", " ").title(),
        "{API_ROUTES}": api_routes,
    }

    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "main_content.py"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}/src/{app_name}", "main.py"))

    print(f"✅ Created FastAPI app structure at {base_dir}")


def generate_pydantic_model(name, fields):
    """Generate a Pydantic model definition."""
    model_str = f"from pydantic import BaseModel, Field\nfrom typing import List, Optional, Literal\nimport time\n\n"
    model_str += f"class {name.capitalize()}(BaseModel):\n"

    for field_name, field_type in fields.items():
        # Skip fields that start with an underscore
        if not field_name.startswith("_"):
            model_str += f"    {field_name}: {field_type}\n"

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
        print(f" ========= model_name = {model_name}")
        api_code = load_template("api_content.py", app_name, model_name, model_name.capitalize())
        api_file = api_dir / f"{model_name.lower()}_api.py"

        replacements = {
            "{app_name}": app_name,
            "{model_name}": model_name,
            "{model-name}": model_name.replace("_", "-"),
            "{ModelName}": model_name.capitalize(),
            "{APP_NAME}": app_name.upper(),
            "{Model Name}": model_name.replace("_", " ").title(),
            "{AppName}": app_name.capitalize(),
            "{App Name}": app_name.replace("_", " ").title(),
        }
        search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "api_content.py"), replacements, api_file)
        # Save model file
        model_file = models_dir / f"{model_name.lower()}.py"
        with open(model_file, "w") as f:
            f.write(model_code)

        print(f"✅ Generated model: {model_file}")
        print(f"✅ Generated API: {api_file}")

    
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "config_content.py"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}/src/{app_name}", "config.py"))
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "pyproject_content.toml"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}", "pyproject.toml"), False)
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "README.md"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}", "README.md"), False)
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "_gitignore"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}", ".gitignore"))
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "Dockerfile"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}", "Dockerfile"), False)
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "auth_util.py"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}/src/{app_name}", "auth_util.py"))
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "error_util_content.py"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}/src/{app_name}", "error_util.py"))
    search_and_replace(os.path.join(f"{TEMPLATE_DIR}", "__init__.py"), replacements, os.path.join(f"{monorepo_root}/apps/{app_name}/src/{app_name}", "__init__.py"))

    # Generate FastAPI application structure
    create_fastapi_application(app_name, monorepo_root, models)
    # create_readme(app_name, monorepo_root)
    print(f"✅ FastAPI application '{app_name}' setup completed!")


def search_and_replace(template_file: str, replacements: dict, output_file: str, replace: bool = True):
    """
    Reads a template file, replaces placeholders with corresponding values from a dictionary,
    and writes the result to an output file.

    :param template_file: Path to the input template file.
    :param replacements: Dictionary of placeholders and their replacements.
    :param output_file: Path to the output file.
    """

    if not replace and os.path.exists(output_file):
        return

    # Ensure the parent directory of the output file exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(template_file, "r") as f:
        content = f.read()

    for key, value in replacements.items():
        content = content.replace(key, value)

    with open(output_file, "w") as f:
        f.write(content)

    print(f"✅ Generated file: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a FastAPI application.")
    parser.add_argument(
        "--app_name",
        required=True,
        help="The name of the FastAPI application to create."
    )
    parser.add_argument(
        "--monorepo_root",
        default="..",
        help="The root directory of the monorepo (default: ..)."
    )
    
    args = parser.parse_args()
    
    app_name = args.app_name.strip()
    monorepo_root = os.path.expanduser(args.monorepo_root.strip())
    
    main(app_name, monorepo_root)