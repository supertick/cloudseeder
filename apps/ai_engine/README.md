# Ai Engine - FastAPI Application

This is a FastAPI application for `ai_engine`.

## 🚀 Installation & Setup

### Create a Virtual Environment
```sh
cd apps
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install Dependencies
```sh
cd ai_engine
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
```

### Run the Application in Docker
```sh
# # run this from above the apps directory
# docker build -t ai_engine -f apps/ai_engine/Dockerfile .
# docker run --rm -p 8000:8000 ai_engine

# # interactively
# docker run --rm -it ai_engine /bin/sh

```


## 🧪 Testing
```sh
python -m ai_engine.main
```

### Run Tests
```sh
pytest
```

### Run Tests with Coverage
```sh
pytest --cov=ai_engine --cov-report html
```