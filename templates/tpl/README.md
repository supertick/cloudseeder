# {App Name} - FastAPI Application

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
pip install -e .

# move to the packages directory and install the desired packages
cd packages/auth
pip install -e .
cd ../packages/database
pip install -e .
cd ../packages/queues
pip install -e .
```

### Run the Application on Bare Metal
```sh
cd apps/{app_name}
python -m uvicorn {app_name}.main:app --reload
```

{App Name} Should be available at http://localhost:8000

### Run the Application in Docker
```sh
# run this from above the apps directory
docker build -t {app_name} -f apps/{app_name}/Dockerfile .
docker run --rm -p 8000:8000 {app_name}

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