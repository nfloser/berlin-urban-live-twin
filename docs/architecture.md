# Architecture

## Architectural goal

Berlin Urban Live Twin is an incremental, knowledge-graph-oriented urban digital twin. External urban-data schemas are kept at system boundaries rather than propagated into the user interface. Each domain is handled by an ingestion agent that retrieves source data, validates and normalises it into an explicit internal model, maps that model to RDF, and contributes to a shared semantic state.

```text
External urban data
        |
        v
Domain-specific clients
        |
        v
Validation / normalisation
        |
        v
Domain models
        |
        v
RDF mapping
        |
        v
Turtle domain exports
        |
        v
Derived-information agent
        |
        v
Integrated RDF publication
        |
        v
Apache Jena Fuseki / TDB2
        |
        v
FastAPI query layer
        |
        v
React / MapLibre presentation
```

## Current domain agents

### Air quality

The air-quality agent retrieves active Berlin monitoring stations and the official hourly Berlin Luftqualitätsindex (LQI). Source payloads are mapped into explicit `AirQualityStation` and `AirQualityIndexObservation` models. RDF separates relatively stable station identity/location from time-dependent LQI observations and links each observation back to its station.

### Weather

The weather agent retrieves a current observation for Berlin through Bright Sky, whose underlying observations are based on open Deutscher Wetterdienst data. The source payload is converted into a `WeatherObservation` before RDF is created for temperature, relative humidity, pressure, wind speed, condition, and observation time.

### Transit

The transit agent consumes the official VBB GTFS-Realtime protocol-buffer feed. It derives an aggregated `TransitSnapshot` containing the number of trip updates, the number and share of delayed trips, and maximum observed delay before producing RDF. Aggregation is deliberately performed inside the domain boundary rather than in the frontend.

## Semantic persistence and query layer

Each source agent still serializes its current RDF output as Turtle into `data/`. These files are intentionally retained because they make agent output easy to inspect, test and debug independently.

After source refresh and derived analysis, the orchestration layer merges the current Turtle outputs and publishes the integrated graph through the SPARQL Graph Store Protocol. The Docker runtime uses Apache Jena Fuseki 6.2.0 with a persistent TDB2 dataset named `/twin`. The TDB database is stored in the `fuseki-data` Docker volume.

The backend repository supports two state sources:

1. **Graph Store mode** — used by the Docker runtime. The integrated graph is retrieved from Fuseki and queried with the established RDFLib/SPARQL query layer.
2. **File-backed mode** — used by deterministic tests and lightweight local development when `TWIN_GRAPH_STORE_URL` is not configured.

This staged migration preserves the existing query behaviour while moving persistence out of flat files. A future optimisation can execute SPARQL queries directly against Fuseki instead of transferring the current default graph into RDFLib for each backend reload.

The backend currently exposes:

- active monitoring stations suitable for spatial presentation;
- current official station-level Berlin LQI observations;
- the latest weather observation;
- the latest aggregated transit observation;
- the latest derived Urban Stress observation;
- source freshness metadata;
- summary information about the integrated graph; and
- the complete current RDF graph in Turtle format.

## Derived information

The analysis agent calculates an experimental Urban Stress Index from three semantically integrated observations: worst current Berlin LQI grade, latest temperature, and latest VBB delayed-trip share.

The calculation is transparent and deterministic rather than predictive. Before deriving a value, the agent checks temporal consistency: the latest source observations may be at most two hours apart. Otherwise no derived observation is emitted. The resulting component values and index are themselves represented in RDF and therefore become queryable semantic state.

## Freshness model

Temporal consistency between inputs and absolute freshness are treated as different concerns.

The backend currently assesses absolute freshness using explicit prototype thresholds:

- air quality: 2 hours;
- weather: 2 hours;
- transit: 15 minutes;
- derived urban stress: 2 hours.

Each domain is reported as `fresh`, `stale`, or `missing` through `GET /freshness`. This prevents the presentation layer from implying that any persisted observation is automatically live merely because it exists.

## Runtime architecture

```text
                         docker compose
                               |
             +-----------------+------------------+
             |                                    |
             v                                    v
       refresh service                      Fuseki service
             |                                    |
 source APIs -> RDF exports                       | TDB2 volume
             |                                    |
             v                                    |
       analysis agent                             |
             |                                    |
             v                                    |
     integrated RDF -- Graph Store PUT ---------->|
                                                  |
                                                  v
                                           persistent /twin
                                                  |
                                                  v
                                           backend service
                                                  |
                                                  v
                                            FastAPI :8000
                                                  |
                                                  v
                                           frontend :8080
```

The frontend communicates only with the backend and therefore has no knowledge of the original external APIs or storage technology.

## Validation strategy

The persistent-store integration is covered at several levels:

- unit tests for Graph Store publication;
- repository tests for remote Graph Store loading;
- Docker image and Compose validation;
- an end-to-end CI check that starts Fuseki, seeds RDF through Graph Store HTTP, starts the backend, and verifies API state and freshness through the real container network.

This keeps infrastructure changes subject to the same test-driven contract as application code.

## Design principles

1. **External schemas remain at the boundary.** JSON and GTFS-Realtime structures are converted into explicit internal models before semantic conversion.
2. **Semantic representation is a first-class concern.** RDF is produced from validated domain objects rather than arbitrary external payloads.
3. **Presentation is decoupled from ingestion.** The frontend consumes a stable backend interface rather than external city APIs.
4. **Derived information is reproducible.** Analytical outputs are deterministic, time-checked, and represented as RDF together with their component values.
5. **Freshness is explicit.** Persisted data is not automatically treated as live; age and source-specific thresholds are observable.
6. **Persistence is standards-based.** The integrated graph is published through standard Graph Store HTTP and served by a SPARQL-capable TDB2 store.
7. **Infrastructure is introduced progressively.** Inspectable Turtle exports remain available while persistent semantic storage is introduced behind a tested repository boundary.
8. **Development is test-driven where practical.** Behavioural changes are specified by automated tests before implementation.
9. **Domain agents remain independently testable.** Each agent owns its models, mappings, dependencies, and tests.

## Relationship to The World Avatar

The project is inspired by architectural concepts used by The World Avatar: domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, persistent semantic storage, and derived information. It is an independent implementation for learning and experimentation rather than a copy of The World Avatar codebase.
