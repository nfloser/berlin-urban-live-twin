import { useEffect, useMemo, useState } from "react";

import MapView from "./MapView";
import {
  fetchAirQuality,
  fetchFreshness,
  fetchStations,
  fetchTransit,
  fetchUrbanStress,
  fetchWeather,
  type AirQualityState,
  type FreshnessState,
  type Station,
  type TransitState,
  type UrbanStressState,
  type WeatherState,
} from "./api";
import { buildStationMapPoints } from "./mapModel";
import "./styles.css";

export default function App() {
  const [stations, setStations] = useState<Station[]>([]);
  const [airQuality, setAirQuality] = useState<AirQualityState | null>(null);
  const [weather, setWeather] = useState<WeatherState | null>(null);
  const [transit, setTransit] = useState<TransitState | null>(null);
  const [urbanStress, setUrbanStress] = useState<UrbanStressState | null>(null);
  const [freshness, setFreshness] = useState<FreshnessState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetchStations(),
      fetchAirQuality(),
      fetchWeather(),
      fetchTransit(),
      fetchUrbanStress(),
      fetchFreshness(),
    ])
      .then(([stationData, airData, weatherData, transitData, stressData, freshnessData]) => {
        setStations(stationData);
        setAirQuality(airData);
        setWeather(weatherData);
        setTransit(transitData);
        setUrbanStress(stressData);
        setFreshness(freshnessData);
      })
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "Unable to load urban twin state.");
      });
  }, []);

  const stationMapPoints = useMemo(
    () => buildStationMapPoints(stations, airQuality),
    [stations, airQuality],
  );

  const freshnessSummary = useMemo(() => {
    if (!freshness) {
      return "Checking source freshness…";
    }
    const entries = Object.values(freshness);
    if (entries.every((entry) => entry.status === "fresh")) {
      return "All sources fresh";
    }
    const stale = entries.filter((entry) => entry.status === "stale").length;
    const missing = entries.filter((entry) => entry.status === "missing").length;
    return `${stale} stale · ${missing} missing`;
  }, [freshness]);

  return (
    <main className="shell">
      <header className="hero">
        <p className="eyebrow">Semantic urban observatory</p>
        <h1>Berlin Urban Live Twin</h1>
        <p>
          A continuously updated view of environmental and mobility conditions,
          integrated through a shared semantic representation.
        </p>
        <p className="freshness-summary">{freshnessSummary}</p>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <section className="metrics" aria-label="Current urban conditions">
        <article className="metric-card">
          <span>Urban stress</span>
          <strong>{urbanStress ? `${urbanStress.index.toFixed(1)} / 100` : "—"}</strong>
          <small>Experimental cross-domain indicator</small>
        </article>

        <article className="metric-card">
          <span>Air quality</span>
          <strong>{airQuality ? `LQI ${airQuality.worst_grade}` : "—"}</strong>
          <small>{airQuality ? `Worst current grade across ${airQuality.stations.length} stations` : "Awaiting official LQI"}</small>
        </article>

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
        <MapView stations={stationMapPoints} />
      </section>
    </main>
  );
}
