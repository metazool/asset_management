# Asset Management System

A Django-based asset management system designed for managing scientific instruments across multiple locations and departments. This system provides role-based access control, maintenance tracking, and calibration management for research facilities and laboratories.

## Features

- **Asset Management**
  - Track instruments across multiple sites and departments
  - Monitor instrument status and location
  - Manage calibration schedules and records
  - Document maintenance activities

- **Calibration Management**
  - Create and manage calibration certificates
  - Track calibration history and due dates
  - Record calibration measurements and results
  - Handle non-conformities and corrective actions
  - Support multiple calibration types (routine, initial, verification, post-repair)

- **Role-Based Access Control**
  - Department-specific permissions
  - Role-based authorization
  - Audit logging of actions
  - User activity tracking

- **API Features**
  - RESTful API with comprehensive endpoints
  - JWT authentication
  - Filtering and search capabilities
  - Pagination support
  - Detailed API documentation

- **DevOps Integration**
  - Docker containerization
  - Kubernetes deployment configurations
  - GitHub Actions CI/CD pipelines
  - Automated testing
  - Code quality checks

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL 15+
- **Authentication**: JWT with dj-rest-auth
- **Documentation**: Sphinx with REST API docs
- **Testing**: pytest with coverage reporting
- **CI/CD**: GitHub Actions
- **Containerization**: Docker, Kubernetes
- **Code Quality**: flake8, black, isort

## Project Structure

```
asset_management/
├── src/
│   └── asset_management/
│       ├── api/            # API endpoints and views
│       ├── assets/         # Asset management models and logic
│       └── users/          # User management and authentication
├── tests/
│   ├── integration/        # Integration tests
│   └── unit/              # Unit tests
├── docs/                   # Documentation
├── k8s/                    # Kubernetes configurations
├── .github/
│   └── workflows/         # GitHub Actions workflows
└── docker-compose.yml     # Docker Compose configuration
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Docker and Docker Compose (optional)
- kubectl (for Kubernetes deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/asset-management.git
   cd asset-management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Docker Development

1. Build and start services:
   ```bash
   docker-compose up --build
   ```

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

### Production Deployment

1. Build the Docker image:
   ```bash
   docker build -t asset-management:latest .
   ```

2. Deploy to Kubernetes:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/postgres.yaml
   kubectl apply -f k8s/django.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

## Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=src/asset_management --cov-report=xml
```

## API Documentation

API documentation is available at `/api/docs/` when running the server. Key endpoints include:

- `/api/instruments/` - Instrument management
- `/api/calibration-certificates/` - Calibration certificate management
- `/api/calibration-records/` - Calibration record management
- `/api/sites/` - Site management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 