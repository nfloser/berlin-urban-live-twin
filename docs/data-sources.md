# Data sources

## Berlin air quality

The air-quality domain uses the official Berlin air quality monitoring network (Berliner Luftgütemessnetz) operated by the Berlin Senate administration.

Public REST documentation: https://luftdaten.berlin.de/api/doc

The current implementation uses:

- `GET https://luftdaten.berlin.de/api/stations`
- `GET https://luftdaten.berlin.de/api/lqis/data`

Station payloads are normalised into an internal monitoring-station model before RDF conversion. The LQI endpoint provides current Berlin short-term air-quality-index observations. These are represented as separate RDF observations linked back to their monitoring station.

The official Berlin LQI is recalculated hourly. It expresses air quality on a school-grade scale from 1 (very good) to 6 (very poor). The station-level LQI is the highest pollutant-specific index class available at that station. The Berlin methodology uses NO2 and O3 one-hour means, CO moving eight-hour means, and PM10/PM2.5 moving 24-hour means when classifying the pollutant-specific sub-indices.

LQI methodology: https://luftdaten.berlin.de/lqi/info

The API also exposes lower-level station and component measurement endpoints. Raw pollutant concentration ingestion remains a future extension; the live prototype currently uses the official calculated LQI rather than reproducing the Berlin authority's rolling-window calculations independently.

## Weather

Current weather observations are retrieved through the public Bright Sky API. Bright Sky provides a JSON interface over open meteorological observations from the Deutscher Wetterdienst (DWD); no API key is required.

The weather agent uses:

- `GET https://api.brightsky.dev/current_weather`
- Berlin reference coordinates: latitude `52.52`, longitude `13.405`

The current semantic representation can include observation time, temperature, relative humidity, mean sea-level pressure, wind speed, and weather condition.

Bright Sky documentation: https://brightsky.dev/

## Public transport

The transit domain uses the official Verkehrsverbund Berlin-Brandenburg (VBB) GTFS-Realtime feed:

- `GET https://production.gtfsrt.vbb.de/data`

The feed is downloaded as a protocol-buffer payload. The transit agent currently derives a city-level operational snapshot from trip updates by calculating:

- total trip updates in the feed;
- trip updates whose maximum arrival/departure delay exceeds 60 seconds;
- the delayed share; and
- maximum observed delay.

The client sends an identifying `User-Agent` as requested by the feed provider. The VBB feed is publicly accessible without authentication and is published under CC BY 4.0. VBB has also documented that parts of realtime coverage may be incomplete because of upstream data limitations; the application therefore treats the feed as an observation source rather than assuming exhaustive system coverage.

Feed information: https://production.gtfsrt.vbb.de/

## Source-integration principle

External source representations are never used as the internal digital-twin model. JSON and GTFS-Realtime payloads terminate at domain boundaries, where validation and mapping produce explicit internal models. Only those internal models are transformed into the shared RDF representation.
