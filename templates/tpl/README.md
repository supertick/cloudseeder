# {AppName} - FastAPI Application

This is a FastAPI application for `{app_name}`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
cd apps/{app_name}
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install Dependencies
```sh
# pip install -r requirements.txt
# for toml files
pip install -e .
```

### Run the Application
```sh
python -m uvicorn {app_name}.main:app --reload

```

## 🧪 Testing

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov={app_name} --cov-report html
```