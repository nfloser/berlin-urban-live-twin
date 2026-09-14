import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import type { Station } from "./api";

interface MapViewProps {
  stations: Station[];
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

    const markers = stations.map((station) =>
      new maplibregl.Marker()
        .setLngLat([station.longitude, station.latitude])
        .setPopup(
          new maplibregl.Popup({ offset: 18 }).setHTML(
            `<strong>${station.name}</strong><br/>Station ${station.code}`,
          ),
        )
        .addTo(map),
    );

    return () => {
      markers.forEach((marker) => marker.remove());
      map.remove();
    };
  }, [stations]);

  return <div ref={containerRef} className="map" aria-label="Map of Berlin air-quality stations" />;
}
