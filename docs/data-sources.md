# Data sources

## Berlin air quality

The first data source is the official Berlin air quality monitoring network (Berliner Luftgütemessnetz) operated by the Berlin Senate administration.

The public REST API exposes station metadata and measurement data. The initial agent increment uses the following endpoints:

- `GET https://luftdaten.berlin.de/api/stations`
- `GET https://luftdaten.berlin.de/api/stations/{code}/data`

The project starts with air-quality data because it provides a well-defined, observable urban domain with geolocated monitoring stations and continuously updated measurements.

Source documentation: https://luftdaten.berlin.de/api/doc

## Weather

Current weather observations are retrieved through the public Bright Sky API. Bright Sky provides a JSON interface over open meteorological data published by the Deutscher Wetterdienst (DWD). No API key is required.

The weather agent currently uses:

- `GET https://api.brightsky.dev/current_weather`
- Berlin reference coordinates: latitude `52.52`, longitude `13.405`

Bright Sky is used as an access layer rather than a primary data producer; the underlying meteorological observations originate from the DWD open-data ecosystem.

Source documentation: https://brightsky.dev/

## Planned mobility source

Public transport will be introduced through the official Verkehrsverbund Berlin-Brandenburg (VBB) GTFS-Realtime feed. This allows the project to integrate a third, operationally different urban domain and later derive cross-domain information from environmental and mobility conditions.
