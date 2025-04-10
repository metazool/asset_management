Welcome to Asset Management System's documentation!
==============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   models
   api
   authentication
   deployment

Introduction
-----------

The Asset Management System is a Django-based application for managing scientific instruments and their calibration records. It provides a comprehensive solution for tracking instruments, their locations, maintenance history, and calibration status.

Features
~~~~~~~~

- User authentication and authorization with role-based access control
- Instrument tracking and management with status monitoring
- Calibration certificate management with version control
- Maintenance record tracking with different types (preventive, corrective, predictive)
- Review system for instruments with priority levels
- Department and location management with site support
- RESTful API for integration with filtering and search capabilities
- Docker support for easy deployment
- GitHub Actions CI/CD pipeline
- Multi-registry container support (GHCR and ECR)

Getting Started
-------------

To get started with the Asset Management System:

1. Clone the repository
2. Set up the development environment
3. Configure the database
4. Run the migrations
5. Start the development server

For detailed instructions, see the :doc:`installation` guide.

Development
----------

The system uses:

- Django 4.2
- Django REST framework
- PostgreSQL 13+
- Python 3.12
- Docker and Docker Compose
- GitHub Actions for CI/CD

Documentation
------------

This documentation is organized into several sections:

- :doc:`introduction`: Overview of the system
- :doc:`installation`: Setup instructions
- :doc:`models`: Database models and relationships including:
  - Sites and Locations
  - Departments
  - Instruments with status tracking
  - Calibration Certificates with versioning
  - Calibration Records
  - Maintenance Records
  - Reviews with priority levels
- :doc:`api`: REST API documentation with filtering and search capabilities
- :doc:`authentication`: User authentication and role-based permissions
- :doc:`deployment`: Deployment options and configuration

API Documentation
----------------

The :doc:`api` section provides detailed documentation of all available API endpoints, including:
- CRUD operations for all models
- Filtering and search capabilities
- Role-based access control
- Special endpoints for certificate review and versioning

Model Documentation
------------------

The :doc:`models` section describes the data models used in the system, including their relationships and constraints.

Authentication
-------------

The :doc:`authentication` section covers user authentication and role-based authorization.

Deployment
---------

The :doc:`deployment` section provides instructions for deploying the system in production.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 