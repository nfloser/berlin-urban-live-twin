# Data sources

## Berlin air quality

The first data source is the official Berlin air quality monitoring network (Berliner Luftgütemessnetz) operated by the Berlin Senate administration.

The public REST API exposes station metadata and measurement data. The initial agent increment uses the following endpoints:

- `GET https://luftdaten.berlin.de/api/stations`
- `GET https://luftdaten.berlin.de/api/stations/{code}/data`

The project starts with air-quality data because it provides a well-defined, observable urban domain with geolocated monitoring stations and continuously updated measurements. Later increments will integrate additional domains such as weather and public transport.

Source documentation: https://luftdaten.berlin.de/api/doc
