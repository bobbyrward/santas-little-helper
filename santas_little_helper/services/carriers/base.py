"""Base carrier scraper infrastructure."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import requests

from santas_little_helper.models import Carrier, OrderStatus


@dataclass
class TrackingResult:
    """Result from fetching tracking information."""

    status: OrderStatus  # mapped status
    last_location: str | None
    estimated_delivery: datetime | None
    raw_status: str  # original carrier status text
    error: str | None = None  # error message if fetch failed


class BaseCarrierScraper(ABC):
    """Abstract base class for carrier-specific scrapers."""

    carrier: Carrier  # class attribute for carrier type

    @abstractmethod
    def get_tracking_url(self, tracking_number: str) -> str:
        """Return the tracking URL for this carrier."""
        pass

    @abstractmethod
    def fetch_tracking(self, tracking_number: str) -> TrackingResult:
        """Fetch and parse tracking information."""
        pass

    def _make_request(self, url: str) -> str:
        """Make HTTP request with standard headers. Returns HTML content."""
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
        response.raise_for_status()
        return response.text

    def _map_status(self, raw_status: str) -> OrderStatus:
        """Map carrier-specific status to OrderStatus enum.

        Default logic:
        - If contains "delivered" -> DELIVERED
        - If contains "out for delivery" -> OUT_FOR_DELIVERY
        - If contains "label created" or "shipping label" -> SHIPPED
        - If contains "exception" or "delay" -> EXCEPTION
        - Otherwise -> IN_TRANSIT
        """
        status_lower = raw_status.lower()

        if "delivered" in status_lower:
            return OrderStatus.DELIVERED
        elif "out for delivery" in status_lower:
            return OrderStatus.OUT_FOR_DELIVERY
        elif "label created" in status_lower or "shipping label" in status_lower:
            return OrderStatus.SHIPPED
        elif "exception" in status_lower or "delay" in status_lower:
            return OrderStatus.EXCEPTION
        else:
            return OrderStatus.IN_TRANSIT
