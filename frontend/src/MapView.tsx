import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import type { StationMapPoint } from "./mapModel";

interface MapViewProps {
  stations: StationMapPoint[];
}

function componentText(components: Record<string, number>): string {
  const entries = Object.entries(components);
  if (entries.length === 0) {
    return "No pollutant sub-indices available";
  }
  return entries.map(([name, grade]) => `${name}: ${grade}`).join(" · ");
}

export default function MapView({ stations }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: containerRef.current,
      center: [13.405, 52.52],
      zoom: 10,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors",
          },
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }],
      },
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");

    const markers = stations.map((station) => {
      const lqiText = station.lqiGrade == null
        ? "No current LQI"
        : `LQI ${station.lqiGrade} — ${station.lqiLabel}`;

      return new maplibregl.Marker()
        .setLngLat([station.longitude, station.latitude])
        .setPopup(
          new maplibregl.Popup({ offset: 18 }).setHTML(
            `<strong>${station.name}</strong><br/>Station ${station.code}<br/>${lqiText}<br/><small>${componentText(station.components)}</small>`,
          ),
        )
        .addTo(map);
    });

    return () => {
      markers.forEach((marker) => marker.remove());
      map.remove();
    };
  }, [stations]);

  return <div ref={containerRef} className="map" aria-label="Map of Berlin air-quality stations with current LQI" />;
}
