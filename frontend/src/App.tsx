import { useEffect, useState } from "react";

import MapView from "./MapView";
import {
  fetchStations,
  fetchTransit,
  fetchWeather,
  type Station,
  type TransitState,
  type WeatherState,
} from "./api";
import "./styles.css";

export default function App() {
  const [stations, setStations] = useState<Station[]>([]);
  const [weather, setWeather] = useState<WeatherState | null>(null);
  const [transit, setTransit] = useState<TransitState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchStations(), fetchWeather(), fetchTransit()])
      .then(([stationData, weatherData, transitData]) => {
        setStations(stationData);
        setWeather(weatherData);
        setTransit(transitData);
      })
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "Unable to load urban twin state.");
      });
  }, []);

  return (
    <main className="shell">
      <header className="hero">
        <p className="eyebrow">Semantic urban observatory</p>
        <h1>Berlin Urban Live Twin</h1>
        <p>
          A continuously updated view of environmental and mobility conditions,
          integrated through a shared semantic representation.
        </p>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <section className="metrics" aria-label="Current urban conditions">
        <article className="metric-card">
          <span>Weather</span>
          <strong>{weather?.temperature_c != null ? `${weather.temperature_c.toFixed(1)} °C` : "—"}</strong>
          <small>
            {weather?.relative_humidity_pct != null
              ? `${weather.relative_humidity_pct.toFixed(0)}% relative humidity`
              : "Awaiting observation"}
          </small>
        </article>

        <article className="metric-card">
          <span>Public transport</span>
          <strong>{transit ? `${(transit.delayed_share * 100).toFixed(1)}% delayed` : "—"}</strong>
          <small>
            {transit ? `${transit.delayed_trip_updates} of ${transit.total_trip_updates} trip updates` : "Awaiting realtime feed"}
          </small>
        </article>

        <article className="metric-card">
          <span>Air monitoring</span>
          <strong>{`${stations.length} active ${stations.length === 1 ? "station" : "stations"}`}</strong>
          <small>Official Berlin monitoring network</small>
        </article>
      </section>

      <section className="map-panel">
        <div className="section-heading">
          <p className="eyebrow">Spatial context</p>
          <h2>Monitoring network</h2>
        </div>
        <MapView stations={stations} />
      </section>
    </main>
  );
}
