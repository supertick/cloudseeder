# Widget - FastAPI Application

This is a FastAPI application for `widget`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
cd apps/widget
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
python -m uvicorn widget.main:app --reload

```

## 🧪 Testing

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov=widget --cov-report html
```