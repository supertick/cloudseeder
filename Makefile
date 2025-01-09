# Variables
BACKEND_DIR := apps/seed-app/backend
FRONTEND_DIR := apps/seed-app/frontend

.PHONY: setup-backend setup-frontend start-backend start-frontend clean

# Task: Set up the backend environment
setup-backend:
	cd $(BACKEND_DIR) && python -m venv venv && chmod +x venv/bin/activate && source venv/bin/activate && pip install -r requirements.txt

# Task: Set up the frontend environment
setup-frontend:
	cd $(FRONTEND_DIR) && yarn install

# Task: Start the backend
start-backend:
	cd $(BACKEND_DIR) && source venv/bin/activate && uvicorn app.main:app --reload

# Task: Start the frontend
start-frontend:
	cd $(FRONTEND_DIR) && yarn dev

# Task: Clean up virtual environments and node_modules
clean:
	rm -rf $(BACKEND_DIR)/venv
	rm -rf $(FRONTEND_DIR)/node_modules
