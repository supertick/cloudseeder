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
cd apps/widget
python -m uvicorn widget.main:app --reload
```

Widget Should be available at http://localhost:8000

### Run the Application in Docker
```sh
# run this from above the apps directory
docker build -t widget -f apps/widget/Dockerfile .
docker run --rm -p 8000:8000 widget

# interactively
docker run --rm -it widget /bin/sh

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