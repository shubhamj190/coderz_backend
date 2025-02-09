
# Go Coderz Platform

A Django-based web application featuring multiple apps (accounts, assessments, communications, competitions, courses, dashboards, helpdesk, projects, etc.) with a modular architecture. This repository uses Django REST Framework, JWT authentication (with Simple JWT), and custom email templates (via send-templated-email) to provide a robust backend for various functionalities.

## Table of Contents

- [Features](#features)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Development Notes](#development-notes)
- [Deployment](#deployment)
- [License](#license)

## Features

- **User Authentication & Authorization**  
  Uses custom user models with role-based authentication (admin, teacher, student) via Django REST Framework and Simple JWT.

- **Modular App Structure**  
  Each functional area (accounts, assessments, communications, etc.) is split into its own Django app with versioned APIs (e.g., `api/v1`, `api/v2`).

- **Email Notifications**  
  Implements password reset and other notifications using templated emails via the `send-templated-email` library.

- **Extensible Architecture**  
  Common functionality (middlewares, permissions, throttling, validators, utilities) are stored in the core module, making it easy to extend the project.


*Note:*  
- **Compiled Python files:**  
  `__pycache__` directories and files ending in `.pyc` are automatically generated and are excluded via **.gitignore**.
- **Environment & Settings:**  
  The `config/settings` directory holds your base, local, and production settings along with environment files.
- **Requirements:**  
  The `requirements` folder contains text files for different deployment environments.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository

Create and Activate a Virtual Environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:

bash
Copy
Edit
pip install -r requirements/base.txt
Set Up Environment Variables:

Create a .env file in config/settings (or at the root, based on your configuration) and add your environment variables (e.g., SECRET_KEY, DEBUG, DATABASE_URL, etc.).

Run Migrations:

bash
Copy
Edit
python manage.py migrate
Collect Static Files (if applicable):

bash
Copy
Edit
python manage.py collectstatic
Running the Application
Start the Django development server:

bash
Copy
Edit
python manage.py runserver
Access the application at http://localhost:8000.

Testing
API Testing:
Use Postman or a similar tool to test API endpoints (see the docs/api_reference.md for details).

Unit Tests:
Run tests using:

bash
Copy
Edit
python manage.py test
Development Notes
Folder Organization:
Each functional area is divided into separate apps (e.g., accounts, assessments, communications, etc.) with versioned APIs (v1, v2, etc.) for easier maintenance and upgrades.

Email Templates:
The accounts/templates/templated_email directory contains email templates used for password resets and notifications.

Integrations:
The integrations folder contains code related to external systems (e.g., Git, IDE, Quest Plus).

Core Functionality:
Shared utilities, permissions, throttling, and validators are located in the core folder.

Deployment
For production deployments, ensure you:

Update the settings in config/settings/production.py.
Set environment variables securely.
Use a production-ready database and web server (e.g., Gunicorn with Nginx).
Configure static file serving and HTTPS.
Refer to docs/setup_guide.md for detailed deployment instructions.

