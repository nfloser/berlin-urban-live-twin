"""HTTP client for the official VBB GTFS-Realtime feed."""

from __future__ import annotations

import requests


class VbbRealtimeClient:
    """Retrieve the VBB GTFS-Realtime feed as protocol-buffer bytes."""

    URL = "https://production.gtfsrt.vbb.de/data"
    USER_AGENT = (
        "berlin-urban-live-twin/0.1 "
        "(+https://github.com/nfloser/berlin-urban-live-twin)"
    )

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: int = 15,
    ) -> None:
        self._session = session or requests.Session()
        self._timeout = timeout

    def fetch(self) -> bytes:
        """Download the current GTFS-Realtime payload."""
        response = self._session.get(
            self.URL,
            headers={"User-Agent": self.USER_AGENT},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.content
