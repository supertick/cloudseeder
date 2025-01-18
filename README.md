# CloudSeeder

CloudSeeder is a modular platform designed to enable seamless application development and deployment across local, containerized, and cloud environments. It provides libraries and a seed application to help you build complex systems from a simple, extensible starting point.

## Key Features

- **Local-First Development**: Develop entirely on local resources using bare-metal implementations, ensuring quick and efficient development cycles.
- **Containerized Transition**: Once the local system is ready, easily transition to containerized builds for testing and production deployment.
- **Cloud-Ready**: Deploy with minimal configuration changes to cloud platforms like AWS, Azure, or GCP.
- **Monorepo Structure**: Organized as a monorepo for easy collaboration and management of core libraries and applications.
- **Abstracted Messaging and File Access**: Use local or cloud-based messaging systems and file storage with consistent APIs.
- **Authentication Support**: Built-in authentication mechanisms for secure operations, including JWT and OAuth2.

## Monorepo Structure

The CloudSeeder repository is structured as follows:

```plaintext
cloudseeder/
├── apps/                  # Applications including the seed app and examples
│   ├── seed-app/          # Starting application with FastAPI backend and Next.js frontend
│   └── examples/          # Example applications for various use cases
├── libs/                  # Core libraries for messaging, file access, and authentication
│   ├── abstract-file-access/
│   ├── messaging/
│   ├── authentication/
│   └── common/
├── tools/                 # Development and deployment tools
│   ├── ci-cd/             # CI/CD configurations and scripts
│   ├── container/         # Container build scripts
│   ├── dev-setup/         # Scripts for local development setup
│   └── scripts/           # Helper scripts
├── docs/                  # Documentation for the project
│   ├── setup-guide.md     # Setup and installation guide
│   ├── api-reference.md   # API documentation
│   └── CONTRIBUTING.md    # Contribution guidelines
└── README.md              # Main README for the CloudSeeder monorepo
```

## Getting Started
### Prerequisites
* Python 3.10+
* Node.js 16+ and Yarn
* Docker (optional, for containerization)
* Git

## Installation
Clone the repository:

```bash
git clone https://github.com/your-repo/cloudseeder.git
cd cloudseeder
```

## Install dependencies for the seed app:

### Backend:

```bash
cd apps/seed-app/backend
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
pip install -r requirements.txt
```

### Frontend:

```bash
cd ../frontend
yarn install
Running the Seed Application
```
## Start the Backend:

```bash
cd apps/seed-app/backend
uvicorn app.main:app --reload
```

## Start the Frontend:

```bash
cd apps/seed-app/frontend
yarn dev
```
Access the application in your browser at http://localhost:3000.

## Contributing
Contributions are welcome! See the CONTRIBUTING.md file for guidelines.

## License
CloudSeeder is licensed under the MIT License. See the LICENSE file for more details.


```bash
cd apps/widget
python -m venv venv
source venv/bin/activate 
pip install -e .
python -m uvicorn widget.main:app --reload

# in root
pip install -e packages/database
pip install -e packages/queues

export PYTHONPATH=$(pwd)
```

try 2 
```bash
cd apps/widget
python -m venv venv
source venv/bin/activate 
pip install -e .
python -m uvicorn widget.main:app --reload

# in root

export PYTHONPATH=$(pwd)


# in root
python -m venv venv
source venv/bin/activate
pip install -e packages/database
pip install -e packages/queues


pip install -e apps/widget

```

```bash
rm -rf venv
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
pip install --upgrade pip setuptools wheel
pip install -e packages/database
pip install -e packages/queues


cd templates
python create_python_app.py
# answer the questions
# widget
# ..
cd ..
cd apps/widget
pip install -e .
python -m uvicorn widget.main:app --reload
```
# scribble

## company
* id
* name
* description
* users[]

## users
* id
* email
* roles[]

## roles
* id
* name
* description
* products[name]

## transcription_request
* id
* files[]

## transcription
* id
* type
* status
* files_path

## transcription_result
* id
* type
* status
* files[]

# metalytics
## users
* id
* email
* roles[]

## roles
* id
* name
* description
* products[name]

## input_library
* id
* user_id
* files []

## run_status
* id
* start_datetime
* end_datetime
* status

## products
* id
* name
* description

## usage
* users[id]
* products_success[id]
* products_fail[id]


## configuration
* port
* work_dir
* log_level


There are certain patterns which exist for any application.
Configuration
Authentication
Authorization
Database
Queues - ability to call custom code in an async or blocking manner
Error Handling
Debug Mode
Even the UI follows a similar pattern - e.g. a login page, a registration page, and a dashboard page.

The ability standardize these patterns across the application gives us a lot of flexibility and allows us to focus on the core functionality of the application.
The "boilerplate" can be improved and generated if there are clear divisions between the generated application and the core business logic.
Interfaces can be created for the configuration, database, queues, and authentication.