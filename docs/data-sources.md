# Data sources

## Berlin air quality

The air-quality domain uses the official Berlin air quality monitoring network (Berliner Luftgütemessnetz) operated by the Berlin Senate administration.

Public REST documentation: https://luftdaten.berlin.de/api/doc

The current implementation uses:

- `GET https://luftdaten.berlin.de/api/stations`

Station payloads provide identifiers, names, geographic coordinates, activity state, address information, station groups, and information about measured components. These values are normalised into an internal station model before RDF conversion.

The API also exposes measurement and Berlin air-quality-index endpoints. Live pollutant/LQI ingestion is intentionally not yet represented in the shared graph and is the next air-quality data increment. Until that contract is implemented and tested, the project does not infer air-quality conditions from station metadata alone.

The underlying Berlin open-data catalogue also publishes current and historical measurements for pollutants including NOx, ozone, carbon monoxide, benzene, sulphur dioxide, PM10, PM2.5, and elemental black carbon.

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
