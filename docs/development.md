# Development approach

## Incremental delivery

The repository is intentionally developed as a sequence of small vertical increments so that architectural evolution remains visible in commit history.

The completed v1 sequence is:

1. Berlin air-quality station ingestion and validation;
2. RDF station representation and SPARQL queries;
3. current weather ingestion as a second independent domain;
4. VBB GTFS-Realtime transit ingestion;
5. transparent cross-domain Urban Stress derivation;
6. FastAPI query layer;
7. React/MapLibre spatial presentation;
8. Dockerised execution and deterministic CI;
9. official Berlin LQI ingestion and station-level map integration;
10. temporal consistency and data-freshness checks;
11. persistent Apache Jena Fuseki/TDB2 storage;
12. direct runtime SPARQL queries;
13. PROV-O source lineage;
14. SHACL validation before publication; and
15. deterministic container integration plus scheduled real-source smoke testing.

## Test-driven development

Behavioural changes use a Red-Green-Refactor cycle where practical. A failing test first describes the intended contract, the smallest implementation satisfies it, and structural cleanup follows without changing external behaviour.

The history deliberately contains test-first commits. Infrastructure changes that do not have a meaningful isolated unit contract are validated through Docker, Compose and end-to-end integration checks.

## Continuous integration

The normal `Tests` workflow is deterministic and runs on pushes to `main` and pull requests. It covers:

- each Python domain-agent suite independently;
- the analysis agent;
- backend repository/API behaviour;
- refresh orchestration, graph publication and SHACL validation;
- frontend unit tests and TypeScript production build;
- Docker Compose validation and all service image builds; and
- a real container integration path from Fuseki through direct SPARQL to FastAPI.

A separate `Live source smoke test` is scheduled daily and can also be launched manually. It reaches the real Berlin air-quality, Bright Sky/DWD and VBB endpoints, runs the complete refresh/analysis/SHACL/publication path and then verifies the live API. This workflow is intentionally separate because third-party availability must not make normal commit CI nondeterministic.

## Data-source boundaries

External JSON and GTFS-Realtime payloads stay at the system boundary. Source clients retrieve data, mappers convert it into internal models, and RDF conversion happens only from validated domain objects. The frontend never consumes third-party source payloads directly.

## Semantic contracts

`ontology/city.ttl` defines the project vocabulary. `ontology/shapes.ttl` defines executable SHACL constraints for runtime graph nodes. PROV-O predicates carry source lineage. Together these provide three separate layers of contract:

- vocabulary and meaning;
- structural/value validation; and
- traceable source origin.

## Persistence strategy

Turtle output remains intentionally visible in `data/` for debugging. Operational runtime state is persisted in Fuseki/TDB2. Refresh writes through the Graph Store Protocol; backend reads use the SPARQL endpoint directly. The repository abstraction retains local-file and Graph-Store modes so tests remain isolated and deterministic.

## Definition of done for v1

A v1 change is considered complete only when its behaviour is covered at the appropriate test level, documentation matches the implementation, Docker builds remain valid, and the deterministic persistent-stack integration test passes. Changes to live-source assumptions additionally need to remain observable through the separate live smoke workflow.
