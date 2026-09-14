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
   +----+------------------+
   |                       |
   v                       v
SPARQL query layer   Derived-information modules
   |
   v
FastAPI backend
   |
   v
React / MapLibre presentation
```

## Current domain agents

### Air quality

The air-quality agent retrieves metadata for Berlin monitoring stations, maps the source payload into an `AirQualityStation` domain model, and produces RDF containing station identity, location, activity state, address, and station category. The agent currently models station metadata only; live pollutant measurements and the Berlin air-quality index are a separate upcoming increment.

### Weather

The weather agent retrieves a current observation for Berlin through Bright Sky, whose underlying observations are based on open Deutscher Wetterdienst data. The source payload is converted into a `WeatherObservation` before RDF is created for temperature, relative humidity, pressure, wind speed, condition, and observation time.

### Transit

The transit agent consumes the official VBB GTFS-Realtime protocol-buffer feed. It derives an aggregated `TransitSnapshot` containing the number of trip updates, the number and share of delayed trips, and maximum observed delay before producing RDF. Aggregation is deliberately performed inside the domain boundary rather than in the frontend.

## Semantic state and query layer

During the current prototype stage, domain agents serialize their RDF output as Turtle files into a shared `data/` directory. The backend reconstructs the integrated graph using RDFLib and queries that graph through SPARQL.

This file-backed state is an intermediate architectural choice. It provides persistence and a clean semantic integration boundary without introducing operational complexity prematurely. A persistent triple store is planned once the ontology, query patterns, and agent boundaries have stabilised.

The backend currently exposes:

- active monitoring stations suitable for spatial presentation;
- the latest weather observation;
- the latest aggregated transit observation;
- summary information about the integrated graph; and
- the complete current RDF graph in Turtle format.

## Derived information

The analysis agent contains an experimental Urban Stress Index that combines normalised air-quality, heat, and transit-delay components. Its calculation is intentionally transparent and deterministic rather than predictive.

The calculation and RDF representation are covered by tests, but the module is not yet connected to the live refresh pipeline. This is intentional: live air-quality-index measurements must first be represented in the shared graph so that the analysis can consume semantically integrated source observations rather than manually supplied values.

## Runtime architecture

```text
                 docker compose
                      |
        +-------------+-------------+
        |                           |
        v                           v
  refresh service              backend service
        |                           |
        | writes RDF                | reads RDF
        v                           v
      data/ <---------------- shared volume
                                    |
                                    v
                              FastAPI :8000
                                    |
                                    v
                              frontend :8080
```

The refresh service executes the domain agents sequentially. The backend mounts the generated RDF state read-only. The frontend communicates only with the backend and therefore has no knowledge of the original external APIs.

## Design principles

1. **External schemas remain at the boundary.** JSON and GTFS-Realtime structures are converted into explicit internal models before semantic conversion.
2. **Semantic representation is a first-class concern.** RDF is produced from validated domain objects rather than arbitrary external payloads.
3. **Presentation is decoupled from ingestion.** The frontend consumes a stable backend interface rather than external city APIs.
4. **Derived information should be reproducible.** Analytical outputs are deterministic and can be represented as RDF together with their component values.
5. **Infrastructure is introduced progressively.** The prototype uses RDFLib and Turtle before a persistent triple store is justified.
6. **Development is test-driven where practical.** Behavioural changes are specified by automated tests before implementation.
7. **Domain agents remain independently testable.** Each agent owns its models, mappings, dependencies, and tests.

## Relationship to The World Avatar

The project is inspired by architectural concepts used by The World Avatar: domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, and derived information. It is an independent implementation for learning and experimentation rather than a copy of The World Avatar codebase.
