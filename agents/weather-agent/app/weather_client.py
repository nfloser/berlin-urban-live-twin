"""Client for current Berlin weather data derived from DWD observations."""

from __future__ import annotations

from typing import Any

import requests


class BrightSkyWeatherClient:
    """Retrieve current weather for central Berlin from Bright Sky."""

    URL = "https://api.brightsky.dev/current_weather"
    BERLIN_LAT = 52.52
    BERLIN_LON = 13.405

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: int = 10,
    ) -> None:
        self._session = session or requests.Session()
        self._timeout = timeout

    def get_current_weather(self) -> Any:
        """Return the current weather payload for Berlin."""
        response = self._session.get(
            self.URL,
            params={"lat": self.BERLIN_LAT, "lon": self.BERLIN_LON},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()
