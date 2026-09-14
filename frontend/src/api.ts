export interface Station {
  code: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface WeatherState {
  observed_at: string;
  temperature_c: number | null;
  relative_humidity_pct: number | null;
}

export interface TransitState {
  observed_at: string;
  total_trip_updates: number;
  delayed_trip_updates: number;
  max_delay_seconds: number;
  delayed_share: number;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Urban twin API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchStations(): Promise<Station[]> {
  return getJson<Station[]>("/stations");
}

export function fetchWeather(): Promise<WeatherState> {
  return getJson<WeatherState>("/weather");
}

export function fetchTransit(): Promise<TransitState> {
  return getJson<TransitState>("/transit");
}
