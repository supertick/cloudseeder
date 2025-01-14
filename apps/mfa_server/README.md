# Mfa Server - FastAPI Application

This is a FastAPI application for `mfa_server`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
cd apps/mfa_server
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
cd apps/mfa_server
python -m uvicorn mfa_server.main:app --reload
```

Mfa Server Should be available at http://localhost:8000

### Run the Application in Docker
```sh
# run this from above the apps directory
docker build -t mfa_server -f apps/mfa_server/Dockerfile .
docker run --rm -p 8000:8000 mfa_server

# interactively
docker run --rm -it mfa_server /bin/sh

```


## 🧪 Testing

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov=mfa_server --cov-report html
```