API Documentation
================

This section provides detailed documentation for the Asset Management System's REST API endpoints.

Authentication
-------------

All API endpoints require authentication using JWT tokens. To authenticate:

1. Obtain a token by sending a POST request to ``/api/auth/token/`` with your credentials
2. Include the token in the Authorization header of subsequent requests: ``Authorization: Bearer <token>``

Endpoints
--------

Instruments
~~~~~~~~~~

.. http:get:: /api/instruments/

   List all instruments.

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "name": "Thermometer",
            "serial_number": "TH-001",
            "model": "TH2000",
            "manufacturer": "ThermoTech",
            "category": "measurement",
            "location": 1,
            "department": 1,
            "status": "active",
            "review_status": "none",
            "last_review_date": null,
            "next_review_date": null
          }
        ]
      }

.. http:post:: /api/instruments/

   Create a new instrument.

   **Request**:

   .. sourcecode:: json

      {
        "name": "Thermometer",
        "serial_number": "TH-001",
        "model": "TH2000",
        "manufacturer": "ThermoTech",
        "category": "measurement",
        "location": 1,
        "department": 1
      }

Calibration Certificates
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/calibration-certificates/

   List all calibration certificates.

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "certificate_number": "CERT-001",
            "version": 1,
            "status": "APPROVED",
            "issue_date": "2024-01-01",
            "expiry_date": "2025-01-01",
            "certificate_type": "ROUTINE",
            "created_by": 1,
            "calibration_data": {
              "temperature": {
                "measured_values": [20.1, 25.2, 30.3],
                "reference_values": [20.0, 25.0, 30.0],
                "correlation_coefficient": 0.999,
                "uncertainty": 0.1
              }
            },
            "reviewer": 2,
            "review_date": "2024-01-02T10:00:00Z",
            "review_notes": "",
            "is_approved": true,
            "non_conformities": [],
            "corrective_actions": []
          }
        ]
      }

.. http:post:: /api/calibration-certificates/

   Create a new calibration certificate.

   **Request**:

   .. sourcecode:: json

      {
        "certificate_number": "CERT-001",
        "issue_date": "2024-01-01",
        "expiry_date": "2025-01-01",
        "certificate_type": "ROUTINE",
        "calibration_data": {
          "temperature": {
            "measured_values": [20.1, 25.2, 30.3],
            "reference_values": [20.0, 25.0, 30.0],
            "correlation_coefficient": 0.999,
            "uncertainty": 0.1
          }
        }
      }

Calibration Records
~~~~~~~~~~~~~~~~~

.. http:get:: /api/calibration-records/

   List all calibration records.

   **Parameters**:
   
   - ``status`` (string): Filter by status
   - ``calibration_type`` (string): Filter by calibration type
   - ``instrument`` (integer): Filter by instrument ID
   - ``search`` (string): Search in description field

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "instrument": 1,
            "date_performed": "2024-01-01",
            "next_calibration_date": "2025-01-01",
            "performed_by": 1,
            "calibration_type": "routine",
            "description": "Annual calibration",
            "status": "completed",
            "certificate": 1,
            "results": {
              "temperature": {
                "measured_value": 25.0,
                "reference_value": 25.0,
                "deviation": 0.0,
                "status": "pass"
              }
            }
          }
        ]
      }

.. http:post:: /api/calibration-records/

   Create a new calibration record.

   **Request**:

   .. sourcecode:: json

      {
        "instrument": 1,
        "date_performed": "2024-01-01",
        "next_calibration_date": "2025-01-01",
        "performed_by": 1,
        "calibration_type": "routine",
        "description": "Annual calibration",
        "results": {
          "temperature": {
            "measured_value": 25.0,
            "reference_value": 25.0,
            "deviation": 0.0,
            "status": "pass"
          }
        }
      }

Sites
~~~~~

.. http:get:: /api/sites/

   List all sites.

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "name": "Main Campus",
            "code": "MC",
            "address": "123 Science Street",
            "contact_email": "contact@campus.edu",
            "contact_phone": "+1-555-0123",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
          }
        ]
      }

.. http:post:: /api/sites/

   Create a new site.

   **Request**:

   .. sourcecode:: json

      {
        "name": "Main Campus",
        "code": "MC",
        "address": "123 Science Street",
        "contact_email": "contact@campus.edu",
        "contact_phone": "+1-555-0123"
      }

.. http:get:: /api/sites/{id}/

   Get a specific site.

   **Response**:

   .. sourcecode:: json

      {
        "id": 1,
        "name": "Main Campus",
        "code": "MC",
        "address": "123 Science Street",
        "city": "Research City",
        "state": "Science State",
        "country": "United States",
        "postal_code": "12345",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "is_active": true
      }

.. http:patch:: /api/sites/{id}/

   Update a site.

   **Request**:

   .. sourcecode:: json

      {
        "name": "Updated Campus",
        "latitude": 41.8781,
        "longitude": -87.6298
      }

.. http:delete:: /api/sites/{id}/

   Delete a site.

   **Response**: 204 No Content

Error Responses
--------------

The API uses standard HTTP status codes to indicate success or failure:

* 200 OK - Request successful
* 201 Created - Resource created successfully
* 400 Bad Request - Invalid request data
* 401 Unauthorized - Authentication required
* 403 Forbidden - Insufficient permissions
* 404 Not Found - Resource not found
* 500 Internal Server Error - Server error

All error responses include a JSON body with an error message:

.. sourcecode:: json

   {
     "error": "Error message description"
   }

Issues
~~~~~~

.. http:get:: /api/issues/

   List all issues.

   **Parameters**:
   
   - ``priority`` (string): Filter by priority (low, medium, high, critical)
   - ``status`` (string): Filter by status (open, in_progress, resolved, closed)
   - ``instrument`` (integer): Filter by instrument ID
   - ``search`` (string): Search in title and description fields

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "title": "Temperature Sensor Malfunction",
            "description": "Sensor showing inconsistent readings",
            "priority": "high",
            "status": "open",
            "instrument": 1,
            "reported_by": 1,
            "assigned_to": 2,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "resolved_at": null
          }
        ]
      }

.. http:post:: /api/issues/

   Create a new issue.

   **Request**:

   .. sourcecode:: json

      {
        "title": "Temperature Sensor Malfunction",
        "description": "Sensor showing inconsistent readings",
        "priority": "high",
        "instrument": 1,
        "assigned_to": 2
      }

Sensor Types
~~~~~~~~~~~

.. http:get:: /api/sensor-types/

   List all sensor types.

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "name": "Temperature",
            "description": "Measures temperature in Celsius",
            "unit": "°C",
            "min_range": -40.0,
            "max_range": 120.0,
            "accuracy": 0.1
          }
        ]
      }

.. http:post:: /api/sensor-types/

   Create a new sensor type.

   **Request**:

   .. sourcecode:: json

      {
        "name": "Temperature",
        "description": "Measures temperature in Celsius",
        "unit": "°C",
        "min_range": -40.0,
        "max_range": 120.0,
        "accuracy": 0.1
      }

Measurement Types
~~~~~~~~~~~~~~~

.. http:get:: /api/measurement-types/

   List all measurement types.

   **Response**:

   .. sourcecode:: json

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 1,
            "name": "Temperature",
            "description": "Temperature measurement",
            "unit": "°C",
            "min_value": -273.15,
            "max_value": 1000.0,
            "precision": 2
          }
        ]
      }

.. http:post:: /api/measurement-types/

   Create a new measurement type.

   **Request**:

   .. sourcecode:: json

      {
        "name": "Temperature",
        "description": "Temperature measurement",
        "unit": "°C",
        "min_value": -273.15,
        "max_value": 1000.0,
        "precision": 2
      } 