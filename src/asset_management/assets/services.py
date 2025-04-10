from typing import Optional
from django.conf import settings
import requests
from .models import Review


class TicketService:
    def __init__(self):
        self.api_url = getattr(settings, "TICKET_API_URL", None)
        self.api_key = getattr(settings, "TICKET_API_KEY", None)
        self.enabled = bool(self.api_url and self.api_key)

    def create_ticket(self, review: Review) -> Optional[dict]:
        """
        Create a ticket in the external system for a review.
        Returns the ticket ID and URL if successful, None otherwise.
        """
        if not self.enabled:
            return None

        try:
            response = requests.post(
                f"{self.api_url}/tickets",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "title": f"Review required for {review.instrument.name}",
                    "description": review.reason,
                    "priority": review.priority,
                    "assignee": (
                        review.assigned_to.email if review.assigned_to else None
                    ),
                    "metadata": {
                        "instrument_id": review.instrument.id,
                        "instrument_name": review.instrument.name,
                        "review_id": review.id,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return {"ticket_id": data["id"], "ticket_url": data["url"]}
        except requests.RequestException:
            return None

    def update_ticket(self, review: Review) -> Optional[dict]:
        """
        Update the ticket status in the external system.
        Returns the updated ticket data if successful, None otherwise.
        """
        if not self.enabled or not review.external_ticket_id:
            return None

        try:
            response = requests.patch(
                f"{self.api_url}/tickets/{review.external_ticket_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "status": review.status,
                    "assignee": (
                        review.assigned_to.email if review.assigned_to else None
                    ),
                },
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
