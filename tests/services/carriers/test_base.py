"""Tests for base carrier scraper infrastructure."""

from datetime import datetime

import pytest

from santas_little_helper.models import Carrier, OrderStatus
from santas_little_helper.services.carriers.base import (
    BaseCarrierScraper,
    TrackingResult,
)


class TestTrackingResult:
    """Tests for TrackingResult dataclass."""

    def test_create_with_all_fields(self):
        """Test creating TrackingResult with all fields."""
        result = TrackingResult(
            status=OrderStatus.IN_TRANSIT,
            last_location="Los Angeles, CA",
            estimated_delivery=datetime(2024, 12, 25, 12, 0, 0),
            raw_status="In Transit",
            error=None,
        )

        assert result.status == OrderStatus.IN_TRANSIT
        assert result.last_location == "Los Angeles, CA"
        assert result.estimated_delivery == datetime(2024, 12, 25, 12, 0, 0)
        assert result.raw_status == "In Transit"
        assert result.error is None

    def test_create_with_error(self):
        """Test creating TrackingResult with error."""
        result = TrackingResult(
            status=OrderStatus.IN_TRANSIT,
            last_location=None,
            estimated_delivery=None,
            raw_status="",
            error="Failed to fetch tracking page",
        )

        assert result.error == "Failed to fetch tracking page"

    def test_create_with_none_optional_fields(self):
        """Test creating TrackingResult with None for optional fields."""
        result = TrackingResult(
            status=OrderStatus.SHIPPED,
            last_location=None,
            estimated_delivery=None,
            raw_status="Label Created",
        )

        assert result.status == OrderStatus.SHIPPED
        assert result.last_location is None
        assert result.estimated_delivery is None
        assert result.error is None  # default value


class TestBaseCarrierScraper:
    """Tests for BaseCarrierScraper abstract class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseCarrierScraper cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            BaseCarrierScraper()

        assert "abstract" in str(exc_info.value).lower()

    def test_map_status_delivered(self):
        """Test _map_status correctly maps delivered statuses."""

        # Create a concrete implementation for testing
        class ConcreteScraper(BaseCarrierScraper):
            carrier = Carrier.FEDEX

            def get_tracking_url(self, tracking_number: str) -> str:
                return f"https://example.com/{tracking_number}"

            def fetch_tracking(self, tracking_number: str) -> TrackingResult:
                return TrackingResult(
                    status=OrderStatus.IN_TRANSIT,
                    last_location=None,
                    estimated_delivery=None,
                    raw_status="",
                )

        scraper = ConcreteScraper()

        # Test various delivered status strings
        assert scraper._map_status("Delivered") == OrderStatus.DELIVERED
        assert scraper._map_status("DELIVERED") == OrderStatus.DELIVERED
        assert scraper._map_status("Package delivered") == OrderStatus.DELIVERED
        assert (
            scraper._map_status("Delivered to front door") == OrderStatus.DELIVERED
        )

    def test_map_status_out_for_delivery(self):
        """Test _map_status correctly maps out for delivery statuses."""

        class ConcreteScraper(BaseCarrierScraper):
            carrier = Carrier.UPS

            def get_tracking_url(self, tracking_number: str) -> str:
                return f"https://example.com/{tracking_number}"

            def fetch_tracking(self, tracking_number: str) -> TrackingResult:
                return TrackingResult(
                    status=OrderStatus.IN_TRANSIT,
                    last_location=None,
                    estimated_delivery=None,
                    raw_status="",
                )

        scraper = ConcreteScraper()

        assert scraper._map_status("Out for Delivery") == OrderStatus.OUT_FOR_DELIVERY
        assert scraper._map_status("OUT FOR DELIVERY") == OrderStatus.OUT_FOR_DELIVERY
        assert (
            scraper._map_status("Package is out for delivery")
            == OrderStatus.OUT_FOR_DELIVERY
        )

    def test_map_status_shipped(self):
        """Test _map_status correctly maps shipped/label created statuses."""

        class ConcreteScraper(BaseCarrierScraper):
            carrier = Carrier.USPS

            def get_tracking_url(self, tracking_number: str) -> str:
                return f"https://example.com/{tracking_number}"

            def fetch_tracking(self, tracking_number: str) -> TrackingResult:
                return TrackingResult(
                    status=OrderStatus.IN_TRANSIT,
                    last_location=None,
                    estimated_delivery=None,
                    raw_status="",
                )

        scraper = ConcreteScraper()

        assert scraper._map_status("Label Created") == OrderStatus.SHIPPED
        assert scraper._map_status("LABEL CREATED") == OrderStatus.SHIPPED
        assert scraper._map_status("Shipping label created") == OrderStatus.SHIPPED
        assert (
            scraper._map_status("Shipping Label Has Been Created")
            == OrderStatus.SHIPPED
        )

    def test_map_status_exception(self):
        """Test _map_status correctly maps exception statuses."""

        class ConcreteScraper(BaseCarrierScraper):
            carrier = Carrier.FEDEX

            def get_tracking_url(self, tracking_number: str) -> str:
                return f"https://example.com/{tracking_number}"

            def fetch_tracking(self, tracking_number: str) -> TrackingResult:
                return TrackingResult(
                    status=OrderStatus.IN_TRANSIT,
                    last_location=None,
                    estimated_delivery=None,
                    raw_status="",
                )

        scraper = ConcreteScraper()

        assert scraper._map_status("Exception") == OrderStatus.EXCEPTION
        assert scraper._map_status("Delivery Exception") == OrderStatus.EXCEPTION
        assert scraper._map_status("Delay") == OrderStatus.EXCEPTION
        assert scraper._map_status("Delayed due to weather") == OrderStatus.EXCEPTION

    def test_map_status_in_transit_default(self):
        """Test _map_status defaults to IN_TRANSIT for unknown statuses."""

        class ConcreteScraper(BaseCarrierScraper):
            carrier = Carrier.ONTRAC

            def get_tracking_url(self, tracking_number: str) -> str:
                return f"https://example.com/{tracking_number}"

            def fetch_tracking(self, tracking_number: str) -> TrackingResult:
                return TrackingResult(
                    status=OrderStatus.IN_TRANSIT,
                    last_location=None,
                    estimated_delivery=None,
                    raw_status="",
                )

        scraper = ConcreteScraper()

        assert scraper._map_status("In Transit") == OrderStatus.IN_TRANSIT
        assert scraper._map_status("In transit to destination") == OrderStatus.IN_TRANSIT
        assert scraper._map_status("Arrived at facility") == OrderStatus.IN_TRANSIT
        assert scraper._map_status("Departed facility") == OrderStatus.IN_TRANSIT
        assert scraper._map_status("Processing") == OrderStatus.IN_TRANSIT
        assert scraper._map_status("Unknown status") == OrderStatus.IN_TRANSIT
