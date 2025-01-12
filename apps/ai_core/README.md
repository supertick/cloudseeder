# Ai Core - FastAPI Application

This is a FastAPI application for `ai_core`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
cd apps/ai_core
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install Dependencies
```sh
pip install -e .
```

### Run the Application
```sh
python -m uvicorn ai_core.main:app --reload
```

Ai Core Should be available at http://localhost:8000

## 🧪 Testing

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov=ai_core --cov-report html
```