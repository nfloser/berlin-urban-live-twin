import { describe, expect, it } from "vitest";

import { buildStationMapPoints } from "./mapModel";


describe("station map model", () => {
  it("joins live LQI observations to monitoring stations", () => {
    const points = buildStationMapPoints(
      [
        { code: "MC010", name: "010 Wedding", latitude: 52.54, longitude: 13.35 },
        { code: "MC174", name: "174 Frankfurter Allee", latitude: 52.51, longitude: 13.47 },
      ],
      {
        observed_at: "2026-09-14T08:00:00+00:00",
        worst_grade: 4,
        stations: [
          { station_code: "MC010", grade: 2, components: { PM10: 2 } },
          { station_code: "MC174", grade: 4, components: { NO2: 4 } },
        ],
      },
    );

    expect(points[0]).toMatchObject({ code: "MC010", lqiGrade: 2, lqiLabel: "good" });
    expect(points[1]).toMatchObject({ code: "MC174", lqiGrade: 4, lqiLabel: "poor" });
  });

  it("keeps stations without a current LQI observation visible", () => {
    const points = buildStationMapPoints(
      [{ code: "MC010", name: "010 Wedding", latitude: 52.54, longitude: 13.35 }],
      null,
    );

    expect(points[0]).toMatchObject({ code: "MC010", lqiGrade: null, lqiLabel: "no current LQI" });
  });
});
