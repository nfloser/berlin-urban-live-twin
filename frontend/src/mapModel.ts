import type { AirQualityState, Station } from "./api";

export interface StationMapPoint extends Station {
  lqiGrade: number | null;
  lqiLabel: string;
  components: Record<string, number>;
}

const LABELS: Record<number, string> = {
  1: "very good",
  2: "good",
  3: "moderate",
  4: "poor",
  5: "very poor",
  6: "extremely poor",
};

export function buildStationMapPoints(
  stations: Station[],
  airQuality: AirQualityState | null,
): StationMapPoint[] {
  const observations = new Map(
    (airQuality?.stations ?? []).map((observation) => [observation.station_code, observation]),
  );

  return stations.map((station) => {
    const observation = observations.get(station.code);
    const lqiGrade = observation?.grade ?? null;
    return {
      ...station,
      lqiGrade,
      lqiLabel: lqiGrade == null ? "no current LQI" : (LABELS[lqiGrade] ?? `grade ${lqiGrade}`),
      components: observation?.components ?? {},
    };
  });
}
