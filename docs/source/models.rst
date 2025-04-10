Models Documentation
===================

This section describes the data models used in the Asset Management System.

Core Models
----------

Instrument
~~~~~~~~~

.. py:class:: asset_management.assets.models.Instrument

   Represents a scientific instrument in the system.

   .. py:attribute:: name
      :type: str

      The name of the instrument.

   .. py:attribute:: serial_number
      :type: str

      The unique serial number of the instrument.

   .. py:attribute:: location
      :type: ForeignKey

      The location where the instrument is stored.

   .. py:attribute:: department
      :type: ForeignKey

      The department that owns the instrument.

   .. py:attribute:: status
      :type: str

      The current status of the instrument (active, inactive, maintenance).

CalibrationCertificate
~~~~~~~~~~~~~~~~~~~~

.. py:class:: asset_management.assets.models.CalibrationCertificate

   Represents a calibration certificate for an instrument.

   .. py:attribute:: certificate_number
      :type: str

      The unique certificate number.

   .. py:attribute:: certificate_type
      :type: str

      The type of certificate (internal/external).

   .. py:attribute:: correlation_data
      :type: JSONField

      The calibration correlation data.

   .. py:attribute:: status
      :type: str

      The current status of the certificate (draft, active, superseded).

   .. py:attribute:: qa_status
      :type: str

      The QA review status (pending, approved, rejected).

CalibrationRecord
~~~~~~~~~~~~~~~~

.. py:class:: asset_management.assets.models.CalibrationRecord

   Represents a calibration record for an instrument.

   .. py:attribute:: instrument
      :type: ForeignKey

      The instrument being calibrated.

   .. py:attribute:: calibration_date
      :type: DateField

      The date when the calibration was performed.

   .. py:attribute:: next_calibration_date
      :type: DateField

      The date when the next calibration is due.

   .. py:attribute:: certificate
      :type: ForeignKey

      The associated calibration certificate.

   .. py:attribute:: results
      :type: JSONField

      The calibration results data.

Supporting Models
---------------

Location
~~~~~~~~

.. py:class:: asset_management.assets.models.Location

   Represents a physical location where instruments are stored.

   .. py:attribute:: name
      :type: str

      The name of the location.

   .. py:attribute:: building
      :type: str

      The building where the location is situated.

   .. py:attribute:: room
      :type: str

      The room number or identifier.

Department
~~~~~~~~~

.. py:class:: asset_management.assets.models.Department

   Represents an organizational department.

   .. py:attribute:: name
      :type: str

      The name of the department.

   .. py:attribute:: code
      :type: str

      The department code.

MaintenanceRecord
~~~~~~~~~~~~~~~~

.. py:class:: asset_management.assets.models.MaintenanceRecord

   Represents a maintenance record for an instrument.

   .. py:attribute:: instrument
      :type: ForeignKey

      The instrument being maintained.

   .. py:attribute:: maintenance_date
      :type: DateField

      The date when maintenance was performed.

   .. py:attribute:: description
      :type: TextField

      Description of the maintenance performed.

   .. py:attribute:: status
      :type: str

      The status of the maintenance (completed, pending, cancelled).

Site
~~~~

.. py:class:: asset_management.assets.models.Site

   Represents a geographic site or facility.

   .. py:attribute:: name
      :type: str

      The name of the site.

   .. py:attribute:: code
      :type: str

      A unique code identifying the site.

   .. py:attribute:: address
      :type: str

      The street address of the site.

   .. py:attribute:: city
      :type: str

      The city where the site is located.

   .. py:attribute:: state
      :type: str

      The state or province where the site is located.

   .. py:attribute:: country
      :type: str

      The country where the site is located.

   .. py:attribute:: postal_code
      :type: str

      The postal or ZIP code of the site.

   .. py:attribute:: latitude
      :type: Decimal

      The geographic latitude of the site.

   .. py:attribute:: longitude
      :type: Decimal

      The geographic longitude of the site.

   .. py:attribute:: is_active
      :type: bool

      Whether the site is currently active.

   .. py:attribute:: created_at
      :type: DateTime

      When the site record was created.

   .. py:attribute:: updated_at
      :type: DateTime

      When the site record was last updated. 