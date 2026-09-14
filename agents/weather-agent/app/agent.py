"""Application service for Berlin weather ingestion."""

from rdflib import Graph

from app.rdf_mapper import weather_to_graph
from app.weather_client import BrightSkyWeatherClient
from app.weather_mapper import map_current_weather


class WeatherAgent:
    """Retrieve and semantically represent the current Berlin weather."""

    def __init__(self, client: BrightSkyWeatherClient | None = None) -> None:
        self._client = client or BrightSkyWeatherClient()

    def refresh(self) -> Graph:
        """Fetch the current weather and return its RDF representation."""
        payload = self._client.get_current_weather()
        observation = map_current_weather(payload)
        return weather_to_graph(observation)
