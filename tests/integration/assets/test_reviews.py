import pytest
from datetime import datetime, timedelta
from rest_framework import status
from asset_management.assets.models import Review, Instrument
from asset_management.users.models import CustomUser as User
from asset_management.assets.services import TicketService


@pytest.mark.integration
@pytest.mark.django_db
def test_create_review(api_client, admin_user, instrument, db):
    """Test creating a new review."""
    api_client.force_authenticate(user=admin_user)

    review_data = {
        "instrument": instrument.id,
        "priority": "high",
        "reason": "Initial review setup",
        "assigned_to": admin_user.id,
        "requested_by": admin_user.id,
        "status": "pending",
    }
    response = api_client.post("/api/reviews/", review_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.count() == 1
    review = Review.objects.first()
    assert review.instrument == instrument
    assert review.priority == "high"
    assert review.reason == "Initial review setup"
    assert review.assigned_to == admin_user


@pytest.mark.integration
@pytest.mark.django_db
def test_update_review_status(api_client, admin_user, instrument, db):
    """Test updating review status."""
    api_client.force_authenticate(user=admin_user)

    # Create initial review
    review = Review.objects.create(
        instrument=instrument,
        requested_by=admin_user,
        priority="high",
        reason="Test review",
        status="pending",
        assigned_to=admin_user,
    )

    # Update status
    update_data = {"status": "in_progress"}
    response = api_client.patch(
        f"/api/reviews/{review.id}/", update_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    review.refresh_from_db()
    assert review.status == "in_progress"


@pytest.mark.integration
@pytest.mark.django_db
def test_complete_review(api_client, admin_user, instrument, db):
    """Test completing a review."""
    api_client.force_authenticate(user=admin_user)

    # Create review
    review = Review.objects.create(
        instrument=instrument,
        requested_by=admin_user,
        priority="high",
        reason="Test review",
        status="in_progress",
        assigned_to=admin_user,
    )

    # Complete review
    complete_data = {
        "status": "completed",
        "reason": "Review completed successfully",
    }
    response = api_client.patch(
        f"/api/reviews/{review.id}/", complete_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    review.refresh_from_db()
    assert review.status == "completed"
    assert review.reason == "Review completed successfully"


@pytest.mark.integration
@pytest.mark.django_db
def test_review_permissions(api_client, admin_user, regular_user, instrument, db):
    """Test review permissions."""
    # Set the regular user's department to match the instrument's department
    regular_user.department = instrument.department
    regular_user.save()

    # Create review as admin
    api_client.force_authenticate(user=admin_user)
    review = Review.objects.create(
        instrument=instrument,
        requested_by=admin_user,
        priority="high",
        reason="Test review",
        status="pending",
        assigned_to=admin_user,
    )

    # Regular user should not be able to update
    api_client.force_authenticate(user=regular_user)
    update_data = {"status": "in_progress"}
    response = api_client.patch(
        f"/api/reviews/{review.id}/", update_data, format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Regular user should be able to view
    response = api_client.get(f"/api/reviews/{review.id}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db
def test_ticket_creation_with_api(api_client, admin_user, instrument, monkeypatch, db):
    """Test creating a ticket from a review using the API."""
    api_client.force_authenticate(user=admin_user)

    # Create review
    review = Review.objects.create(
        instrument=instrument,
        requested_by=admin_user,
        priority="high",
        reason="Test review",
        status="pending",
        assigned_to=admin_user,
    )

    # Mock the ticket service
    def mock_create_ticket(self, review):
        return {
            "ticket_id": "TEST-123",
            "ticket_url": "http://example.com/tickets/TEST-123",
        }

    monkeypatch.setattr(TicketService, "create_ticket", mock_create_ticket)

    # Create ticket
    ticket_data = {
        "title": "Maintenance required",
        "description": "Found issues during review",
        "priority": "high",
        "status": "open",
        "assigned_to": admin_user.id,
    }
    response = api_client.post(
        f"/api/reviews/{review.id}/create-ticket/", ticket_data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    review.refresh_from_db()
    assert review.external_ticket_id == "TEST-123"
    assert review.external_ticket_url == "http://example.com/tickets/TEST-123"


@pytest.mark.integration
@pytest.mark.django_db
def test_ticket_creation_with_service(api_client, instrument, monkeypatch, admin_user):
    """Test creating a ticket from a review using the ticket service."""
    api_client.force_authenticate(user=admin_user)

    # Mock the ticket service
    def mock_create_ticket(self, review):
        return {
            "ticket_id": "TEST-123",
            "ticket_url": "http://example.com/tickets/TEST-123",
        }

    monkeypatch.setattr(TicketService, "create_ticket", mock_create_ticket)

    # Create review
    data = {
        "instrument": instrument.id,
        "reason": "Test review with ticket",
        "priority": "high",
        "requested_by": admin_user.id,
        "assigned_to": admin_user.id,
        "status": "pending",
    }
    response = api_client.post("/api/reviews/", data)
    assert response.status_code == status.HTTP_201_CREATED
    review = Review.objects.first()

    # Create ticket
    ticket_data = {
        "title": "Maintenance required",
        "description": "Found issues during review",
        "priority": "high",
        "status": "open",
        "assigned_to": admin_user.id,
    }
    response = api_client.post(
        f"/api/reviews/{review.id}/create-ticket/", ticket_data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Verify ticket was created
    review.refresh_from_db()
    assert review.external_ticket_id == "TEST-123"
    assert review.external_ticket_url == "http://example.com/tickets/TEST-123"
