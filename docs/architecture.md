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
Shared semantic state
        |
   +----+--------------------+
   |                         |
   v                         v
SPARQL query layer      Analysis agent
   |                         |
   |                   derived RDF
   +-----------+-------------+
               |
               v
         FastAPI backend
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

## Semantic state and query layer

During the current prototype stage, domain agents serialize their RDF output as Turtle files into a shared `data/` directory. The backend reconstructs the integrated graph using RDFLib and queries that graph through SPARQL.

This file-backed state is an intermediate architectural choice. It keeps the semantic model inspectable and version-independent while the ontology and agent contracts are still evolving. A persistent SPARQL/triple-store service is the next infrastructure evolution once the existing file-backed behaviour is preserved by integration tests.

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
        +-------------+-------------+
        |                           |
        v                           v
  refresh service              backend service
        |                           |
        | source RDF                | reads/query RDF
        v                           v
      data/ <---------------- shared volume
        |
        v
  analysis agent
        |
        v
 urban-stress.ttl
                                    |
                                    v
                              FastAPI :8000
                                    |
                                    v
                              frontend :8080
```

The refresh service executes air quality, weather, and transit ingestion before running the analysis agent over those persisted domain outputs. The backend mounts the generated semantic state read-only. The frontend communicates only with the backend and therefore has no knowledge of the original external APIs.

## Design principles

1. **External schemas remain at the boundary.** JSON and GTFS-Realtime structures are converted into explicit internal models before semantic conversion.
2. **Semantic representation is a first-class concern.** RDF is produced from validated domain objects rather than arbitrary external payloads.
3. **Presentation is decoupled from ingestion.** The frontend consumes a stable backend interface rather than external city APIs.
4. **Derived information is reproducible.** Analytical outputs are deterministic, time-checked, and represented as RDF together with their component values.
5. **Freshness is explicit.** Persisted data is not automatically treated as live; age and source-specific thresholds are observable.
6. **Infrastructure is introduced progressively.** RDFLib/Turtle establishes behaviour before migration to a persistent triple store.
7. **Development is test-driven where practical.** Behavioural changes are specified by automated tests before implementation.
8. **Domain agents remain independently testable.** Each agent owns its models, mappings, dependencies, and tests.

## Relationship to The World Avatar

The project is inspired by architectural concepts used by The World Avatar: domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, and derived information. It is an independent implementation for learning and experimentation rather than a copy of The World Avatar codebase.
