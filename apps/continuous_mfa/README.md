# Continuous Mfa - FastAPI Application

This is a FastAPI application for `continuous_mfa`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install Dependencies
```sh
cd apps/continuous_mfa
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
cd apps/continuous_mfa
python -m uvicorn continuous_mfa.main:app --reload
```

Continuous Mfa Should be available at http://localhost:8000

### Run the Application in Docker Locally
```sh
# run this from above the apps directory
docker build -t continuous_mfa -f apps/continuous_mfa/Dockerfile .
docker run --env-file .env --rm --name continuous_mfa -p 8000:8000 continuous_mfa

# interactively
docker run --env-file .env --rm -it continuous_mfa /bin/sh

```


## 🧪 Testing

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov=continuous_mfa --cov-report html
```