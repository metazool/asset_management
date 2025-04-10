import pytest
from django.core.exceptions import ValidationError
from asset_management.assets.models import SensorType, MeasurementType, Instrument
from django.utils import timezone
from decimal import Decimal


@pytest.mark.django_db
def test_sensor_type_creation():
    """Test creating a sensor type with valid data."""
    sensor = SensorType.objects.create(
        name="Temperature Sensor",
        unit="°C",
        min_range=0.0,
        max_range=100.0,
        accuracy=0.5,
    )
    assert sensor.name == "Temperature Sensor"
    assert sensor.unit == "°C"
    assert sensor.min_range == Decimal("0.000")
    assert sensor.max_range == Decimal("100.000")
    assert sensor.accuracy == Decimal("0.50")


@pytest.mark.django_db
def test_sensor_type_validation():
    """Test validation of sensor type data."""
    sensor = SensorType(
        name="Invalid Sensor", unit="°C", min_range=100.0, max_range=0.0, accuracy=0.5
    )
    with pytest.raises(ValidationError):
        sensor.full_clean()


@pytest.mark.django_db
def test_measurement_type_creation():
    """Test creating a measurement type with valid data."""
    measurement = MeasurementType.objects.create(
        name="Temperature Measurement",
        standard="ISO 17025",
        description="Temperature measurement according to ISO 17025",
    )
    assert measurement.name == "Temperature Measurement"
    assert measurement.standard == "ISO 17025"
    assert "ISO 17025" in measurement.description


@pytest.mark.django_db
def test_instrument_with_sensors_and_measurements(instrument, location, department):
    """Test adding sensors and measurements to an instrument."""
    # Create sensor types
    temp_sensor = SensorType.objects.create(
        name="Temperature Sensor",
        unit="°C",
        min_range=0.0,
        max_range=100.0,
        accuracy=0.5,
    )
    pressure_sensor = SensorType.objects.create(
        name="Pressure Sensor",
        unit="Pa",
        min_range=0.0,
        max_range=100000.0,
        accuracy=0.1,
    )

    # Create measurement types
    temp_measurement = MeasurementType.objects.create(
        name="Temperature Measurement", standard="ISO 17025"
    )
    pressure_measurement = MeasurementType.objects.create(
        name="Pressure Measurement", standard="ISO 17025"
    )

    # Add sensors and measurements to instrument
    instrument.sensor_types.add(temp_sensor, pressure_sensor)
    instrument.measurement_types.add(temp_measurement, pressure_measurement)
    instrument.resolution = Decimal("0.01")
    instrument.save()

    # Refresh from database
    instrument.refresh_from_db()

    # Verify relationships
    assert instrument.sensor_types.count() == 2
    assert instrument.measurement_types.count() == 2
    assert instrument.resolution == Decimal("0.01")
    assert temp_sensor in instrument.sensor_types.all()
    assert pressure_sensor in instrument.sensor_types.all()
    assert temp_measurement in instrument.measurement_types.all()
    assert pressure_measurement in instrument.measurement_types.all()


@pytest.mark.django_db
def test_instrument_review_date_validation(instrument):
    """Test validation of review dates."""
    instrument.last_review_date = timezone.now()
    instrument.next_review_date = instrument.last_review_date - timezone.timedelta(
        days=1
    )

    with pytest.raises(ValidationError):
        instrument.full_clean()
