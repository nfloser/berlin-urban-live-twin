"""HTTP client for the official Berlin air quality REST API."""

from __future__ import annotations

from typing import Any

import requests


class BerlinAirQualityClient:
    """Small client for retrieving station metadata and measurements."""

    BASE_URL = "https://luftdaten.berlin.de/api"

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: int = 10,
    ) -> None:
        self._session = session or requests.Session()
        self._timeout = timeout

    def get_stations(self) -> Any:
        """Return metadata for all monitoring stations."""
        return self._get("/stations")

    def get_station_data(self, station_code: str) -> Any:
        """Return measurements for a monitoring station."""
        code = station_code.strip().upper()
        if not code:
            raise ValueError("station_code must not be empty")
        return self._get(f"/stations/{code}/data")

    def get_lqi_data(self) -> Any:
        """Return the current official Berlin air-quality index data."""
        return self._get("/lqis/data")

    def _get(self, path: str) -> Any:
        response = self._session.get(
            f"{self.BASE_URL}{path}",
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()
