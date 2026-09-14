# Architecture

## Architectural goal

Berlin Urban Live Twin is a knowledge-graph-oriented urban digital twin. External urban-data schemas stay at system boundaries. Each ingestion domain retrieves source data, validates and normalises it into explicit internal models, maps those models to RDF, records provenance, and contributes to a shared semantic state.

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
RDF + PROV-O mapping
        |
        v
Turtle domain exports
        |
        v
Derived-information agent
        |
        v
SHACL validation
        |
        v
Graph Store publication
        |
        v
Apache Jena Fuseki / TDB2
        |
        v
Direct SPARQL query layer
        |
        v
FastAPI
        |
        v
React / MapLibre
```

## Domain agents

### Air quality

The air-quality agent retrieves active Berlin monitoring stations and the official hourly Berlin Luftqualitätsindex (LQI). Source payloads become explicit `AirQualityStation` and `AirQualityIndexObservation` models. RDF separates stable station identity/location from time-dependent LQI observations and links observations back to their station. LQI observations record the official Berlin API as their PROV-O source.

### Weather

The weather agent retrieves a current Berlin observation through Bright Sky. Bright Sky provides access to open Deutscher Wetterdienst observations. The domain model captures time, temperature, relative humidity, pressure, wind and condition. The RDF observation records Bright Sky as its direct derivation source and DWD as the primary upstream source.

### Transit

The transit agent consumes the official VBB GTFS-Realtime feed. It derives an explicit `TransitSnapshot` containing total trip updates, delayed updates, delayed share and maximum observed delay. Aggregation occurs inside the domain boundary rather than in the frontend. The resulting observation records the VBB feed through PROV-O.

## Derived information

The analysis agent calculates the experimental Urban Stress Index from three semantically integrated quantities: worst current Berlin LQI grade, latest temperature and latest VBB delayed-trip share.

The calculation is deterministic and transparent. It rejects source combinations whose newest timestamps differ by more than two hours. The resulting RDF observation records its component values and the three external source datasets from which the derivation ultimately originates.

## Semantic validation

RDF syntax alone is not considered sufficient. `ontology/shapes.ttl` defines SHACL constraints for all runtime node types.

The refresh order is:

```text
source refresh
    -> domain RDF
    -> Urban Stress derivation
    -> integrated graph
    -> SHACL validation
    -> persistent publication
```

Publication is skipped when SHACL validation fails. This means a malformed new refresh cannot replace the previously published graph.

## Persistence and query layer

Each agent writes its current RDF output to `data/` as Turtle. These files remain inspectable and make agent-level behaviour easy to debug.

Operational persistence uses Apache Jena Fuseki with TDB2. The refresh process replaces the current default graph through the SPARQL Graph Store Protocol. The persistent dataset is `/twin` and the TDB2 database lives in the `fuseki-data` Docker volume.

The backend repository has three access modes:

1. **Direct SPARQL mode** — the Docker runtime executes normal API queries directly against `/twin/sparql`, avoiding complete graph downloads.
2. **Graph Store compatibility mode** — downloads Turtle from a Graph Store endpoint when direct SPARQL is not configured.
3. **File-backed mode** — loads local Turtle files for deterministic unit tests and lightweight debugging.

The complete graph is intentionally materialised only for explicit graph export use cases such as `GET /graph`.

## API responsibilities

The FastAPI layer exposes:

- liveness and semantic-store readiness;
- active monitoring stations for spatial presentation;
- current official station-level Berlin LQI observations;
- latest weather and transit observations;
- latest derived Urban Stress observation;
- source freshness classifications;
- PROV-O lineage summaries;
- graph statistics; and
- the RDF graph export.

The frontend consumes this stable application API and has no direct dependency on Berlin, DWD/Bright-Sky, VBB or Fuseki APIs.

## Freshness and readiness

Temporal consistency during derivation and absolute freshness during presentation are separate concerns.

Current freshness thresholds are:

- air quality: 2 hours;
- weather: 2 hours;
- transit: 15 minutes;
- Urban Stress: 2 hours.

`GET /freshness` reports `fresh`, `stale` or `missing` per domain. `GET /health` tests process liveness only. `GET /ready` additionally verifies that the semantic store is queryable, non-empty and contains all required observation classes.

## Runtime architecture

```text
                         docker compose
                               |
       +-----------------------+-----------------------+
       |                                               |
       v                                               v
 refresh service                                  Fuseki/TDB2
       |                                               |
 source APIs                                          | persistent volume
       |                                               |
 domain RDF + PROV-O                                  |
       |                                               |
 analysis                                              |
       |                                               |
 SHACL gate                                            |
       |                                               |
       +----------- Graph Store PUT ------------------>| 
                                                       |
                                                       v
                                                  /twin dataset
                                                       |
                                                direct SPARQL
                                                       |
                                                       v
                                                   backend
                                                       |
                                                       v
                                                 FastAPI :8000
                                                       |
                                                       v
                                                frontend :8080
```

## Verification strategy

The architecture is verified at multiple levels. Independent unit suites test source mapping, domain models and semantic mapping. Backend tests exercise SPARQL query behaviour. Orchestration tests verify refresh order, SHACL gating and graph publication. Frontend tests and the production build validate the presentation layer. Container CI starts Fuseki, seeds a complete semantic fixture, starts the backend and exercises the complete persistent API surface. A separate scheduled live-source workflow runs the real external APIs through the same refresh/publish/query path.

## Design principles

1. External source schemas terminate at domain boundaries.
2. RDF is generated from validated internal models, not raw payloads.
3. Semantic constraints are executable through SHACL.
4. Observation lineage is queryable through PROV-O.
5. Derived information is transparent, deterministic and time-checked.
6. Freshness and readiness are explicit rather than implied.
7. Runtime persistence and query access use standard RDF/SPARQL protocols.
8. The UI is decoupled from ingestion and storage technology.
9. Infrastructure changes are protected by integration tests.
10. Domain agents remain independently testable.

## Relationship to The World Avatar

The project is inspired by architectural concepts used by The World Avatar: domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, persistent semantic storage and derived information. It is an independent implementation for learning and experimentation rather than a copy of The World Avatar codebase.
