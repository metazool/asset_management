Deployment Guide
===============

This guide covers the deployment options for the Asset Management System.

Container Deployment
------------------

The system can be deployed using Docker containers. We provide two container registry options:

GitHub Container Registry (GHCR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default deployment option uses GitHub Container Registry. Images are automatically built and pushed on:

- Pushes to the main branch
- Changes to the Dockerfile or source code
- Manual workflow triggers

Images are tagged with:
- Branch name
- PR number (if applicable)
- Semantic version (if available)
- Git SHA

Amazon ECR (Optional)
~~~~~~~~~~~~~~~~~~~~

For EKS deployments, the system can be configured to push to Amazon ECR. This requires:

1. AWS credentials configured in repository secrets:
   - ``AWS_ACCESS_KEY_ID``
   - ``AWS_SECRET_ACCESS_KEY``
   - ``AWS_REGION``

2. Manual workflow trigger with ``push_to_eks: true``

Continuous Integration
--------------------

The system uses GitHub Actions for CI/CD with the following workflows:

CI Workflow
~~~~~~~~~~

Runs on every push and pull request:
- Python 3.12 environment
- PostgreSQL database setup
- Test execution using pytest
- Coverage reporting
- Documentation building

Container Workflow
~~~~~~~~~~~~~~~~

Handles container building and deployment:
- Automatic builds on source changes
- Multi-platform support via Docker Buildx
- Optional EKS deployment configuration
- Automated version tagging

Prerequisites
------------

For local deployment:
- Docker and Docker Compose
- PostgreSQL 13+
- Python 3.12

For cloud deployment:
- Container registry access (GHCR or ECR)
- Kubernetes cluster (for EKS deployment)
- Proper network configuration

Configuration
------------

Environment Variables
~~~~~~~~~~~~~~~~~~~

Required environment variables:
- ``DATABASE_URL``: PostgreSQL connection string
- ``SECRET_KEY``: Django secret key
- ``DEBUG``: Set to False in production
- ``ALLOWED_HOSTS``: List of allowed hostnames

Optional environment variables:
- ``AWS_ACCESS_KEY_ID``: For ECR access
- ``AWS_SECRET_ACCESS_KEY``: For ECR access
- ``AWS_REGION``: For ECR access

Database Setup
-------------

1. Create PostgreSQL database
2. Run migrations::

   python manage.py migrate

3. Create superuser::

   python manage.py createsuperuser

4. Load initial data (if needed)::

   python manage.py loaddata initial_data.json

Production Checklist
------------------

Before deploying to production:

1. Set ``DEBUG=False``
2. Configure proper ``ALLOWED_HOSTS``
3. Set up SSL/TLS
4. Configure proper database backups
5. Set up monitoring and logging
6. Configure proper user permissions
7. Test backup and restore procedures 