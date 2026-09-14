import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

vi.mock("./MapView", () => ({
  default: () => <div data-testid="map-view">Map</div>,
}));

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Berlin Urban Live Twin dashboard", () => {
  it("presents live cross-domain state and freshness from the backend", async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith("/stations")) {
        return { ok: true, json: async () => [{ code: "MC010", name: "010 Wedding", latitude: 52.54, longitude: 13.35 }] };
      }
      if (url.endsWith("/air-quality")) {
        return { ok: true, json: async () => ({ observed_at: "2026-09-14T08:00:00+00:00", worst_grade: 3, stations: [{ station_code: "MC010", grade: 3, components: { O3: 3 } }] }) };
      }
      if (url.endsWith("/weather")) {
        return { ok: true, json: async () => ({ observed_at: "2026-09-14T08:00:00+00:00", temperature_c: 18.2, relative_humidity_pct: 63 }) };
      }
      if (url.endsWith("/transit")) {
        return { ok: true, json: async () => ({ observed_at: "2026-09-14T08:00:00+00:00", total_trip_updates: 200, delayed_trip_updates: 40, max_delay_seconds: 420, delayed_share: 0.2 }) };
      }
      if (url.endsWith("/freshness")) {
        return { ok: true, json: async () => ({
          air_quality: { status: "fresh", observed_at: "2026-09-14T08:00:00+00:00", age_seconds: 600, threshold_seconds: 7200 },
          weather: { status: "fresh", observed_at: "2026-09-14T08:00:00+00:00", age_seconds: 600, threshold_seconds: 7200 },
          transit: { status: "fresh", observed_at: "2026-09-14T08:00:00+00:00", age_seconds: 120, threshold_seconds: 900 },
          urban_stress: { status: "fresh", observed_at: "2026-09-14T08:00:00+00:00", age_seconds: 120, threshold_seconds: 7200 },
        }) };
      }
      return { ok: true, json: async () => ({ observed_at: "2026-09-14T08:00:00+00:00", index: 31, air_quality_component: 0.4, heat_component: 0, transit_component: 0.4 }) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(screen.getByRole("heading", { name: /Berlin Urban Live Twin/i })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("18.2 °C")).toBeInTheDocument());
    expect(screen.getByText("All sources fresh")).toBeInTheDocument();
    expect(screen.getByText("LQI 3")).toBeInTheDocument();
    expect(screen.getByText("31.0 / 100")).toBeInTheDocument();
    expect(screen.getByText("20.0% delayed")).toBeInTheDocument();
    expect(screen.getByText("1 active station")).toBeInTheDocument();
    expect(screen.getByTestId("map-view")).toBeInTheDocument();
  });
});
