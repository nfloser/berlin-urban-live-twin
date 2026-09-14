import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchStations, fetchTransit, fetchWeather } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("urban twin API client", () => {
  it("loads map-ready monitoring stations", async () => {
    const stations = [{ code: "MC010", name: "010 Wedding", latitude: 52.54, longitude: 13.35 }];
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => stations });
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchStations()).resolves.toEqual(stations);
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/stations");
  });

  it("loads the latest weather observation", async () => {
    const weather = { observed_at: "2026-09-14T08:00:00+00:00", temperature_c: 18.2, relative_humidity_pct: 63 };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => weather }));

    await expect(fetchWeather()).resolves.toEqual(weather);
  });

  it("loads the latest transit observation", async () => {
    const transit = { observed_at: "2026-09-14T08:00:00+00:00", total_trip_updates: 200, delayed_trip_updates: 40, max_delay_seconds: 420, delayed_share: 0.2 };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => transit }));

    await expect(fetchTransit()).resolves.toEqual(transit);
  });
});
