# Ai Core - FastAPI Application

This is a FastAPI application for `ai_core`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
cd apps
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install Dependencies
```sh
cd ai_core
pip install -e .

# move to the packages directory and install the desired packages
cd ../../packages/auth
pip install -e .
cd ../database
pip install -e .
cd ../queues
pip install -e .
```

### Run the Application on Bare Metal
```sh
cd apps/ai_core
python -m uvicorn ai_core.main:app --reload
```

Ai Core Should be available at http://localhost:8000

### Run the Application in Docker
```sh
# run this from above the apps directory
docker build -t ai_core -f apps/ai_core/Dockerfile .
docker run --rm -p 8000:8000 ai_core

# interactively
docker run --rm -it ai_core /bin/sh

```


## 🧪 Testing

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov=ai_core --cov-report html
```