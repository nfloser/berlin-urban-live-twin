# Berlin Urban Live Twin

An urban digital twin reference implementation that integrates real-world Berlin data into a persistent semantic knowledge graph for cross-domain environmental and mobility analysis.

## Objective

Berlin Urban Live Twin demonstrates how heterogeneous city data can be treated as one queryable semantic state instead of a collection of unrelated dashboard APIs. Domain agents isolate external source schemas, validate and normalise observations, convert them to RDF, and publish the integrated state into a persistent Apache Jena Fuseki/TDB2 knowledge graph.

The repository is intentionally developed in observable increments. The commit history shows the evolution from individual source clients to semantic integration, persistent SPARQL storage, derived information, validation, provenance, API access, spatial presentation, and end-to-end integration tests.

## v1 capabilities

The v1 reference implementation integrates four semantic domains:

- **Air quality:** active monitoring stations plus the official hourly Berlin Luftqualitätsindex (LQI).
- **Weather:** current Berlin observations through Bright Sky, based on open Deutscher Wetterdienst data.
- **Public transport:** the official VBB GTFS-Realtime feed reduced to an explicit city-level delay snapshot.
- **Derived information:** a transparent experimental Urban Stress Index combining LQI, temperature and transit disruption.

Every refresh follows the same controlled path:

```text
External APIs
    |
    v
source-specific clients
    |
    v
validated domain models
    |
    v
RDF mappings + PROV-O lineage
    |
    v
Turtle exports
    |
    v
cross-domain analysis
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
    +---- direct SPARQL queries ----> FastAPI ----> React / MapLibre
```

Turtle files remain inspectable export/debug artefacts. The Docker runtime reads operational state directly through the Fuseki SPARQL endpoint instead of downloading the complete graph for every API request.

## Semantic quality and provenance

The integrated graph is validated against [`ontology/shapes.ttl`](ontology/shapes.ttl) before it can replace the persistent graph. SHACL constraints cover required properties, datatypes and bounded values for stations, LQI, weather, transit and derived Urban Stress observations.

Observations also carry W3C PROV-O lineage. The API endpoint `GET /provenance` queries this lineage from the graph itself and reports which observation types were derived from which external sources.

## Experimental Urban Stress Index

The Urban Stress Index is deliberately interpretable rather than predictive:

```text
UrbanStress = 100 * (0.40 * air_quality + 0.30 * heat + 0.30 * transit)
```

Air-quality stress uses the worst current official Berlin LQI station grade, heat stress uses current temperature, and transit stress uses the share of delayed VBB trip updates. The analysis refuses to emit a value if the newest source observations are more than two hours apart.

The index is an engineering demonstrator for cross-domain semantic derivation. It is not an official health, mobility or policy metric.

## Freshness and service health

Persisted data is never assumed to be live merely because it exists. `GET /freshness` classifies observations using source-specific thresholds:

- air quality: 2 hours;
- weather: 2 hours;
- transit: 15 minutes;
- Urban Stress: 2 hours.

`GET /health` is a lightweight process-liveness endpoint. `GET /ready` additionally verifies that the semantic store is queryable, non-empty and contains observations for all required domains.

## Runtime

Build and start the persistent store:

```bash
docker compose up -d fuseki
```

Refresh all real source domains, derive cross-domain information, validate the integrated RDF graph and publish it:

```bash
docker compose run --rm refresh
```

Start API and frontend:

```bash
docker compose up -d backend frontend
```

Runtime endpoints:

```text
Frontend            http://localhost:8080
FastAPI             http://localhost:8000
OpenAPI             http://localhost:8000/docs
Fuseki              http://localhost:3030
SPARQL               http://localhost:3030/twin/sparql
Graph Store          http://localhost:3030/twin/data
```

Useful API routes:

```text
GET /health
GET /ready
GET /state
GET /freshness
GET /provenance
GET /stations
GET /air-quality
GET /weather
GET /transit
GET /urban-stress
GET /graph
```

## Repository structure

```text
agents/
  air-quality-agent/
  weather-agent/
  transit-agent/
  analysis-agent/
backend/
frontend/
fuseki/
ontology/
  city.ttl
  shapes.ttl
docs/
scripts/
data/
.github/workflows/
docker-compose.yml
```

Each domain agent owns its source client, source-to-domain mapping, models, RDF mapping and tests. External JSON and Protocol Buffer schemas therefore terminate at domain boundaries rather than leaking into the semantic model or frontend.

## Verification strategy

The normal `Tests` workflow is deterministic. It runs all independent Python suites, backend/SPARQL tests, orchestration and SHACL tests, frontend tests and production build, Docker builds, and a container integration test that exercises Fuseki -> SPARQL -> FastAPI using a deterministic semantic fixture.

A separate scheduled `Live source smoke test` exercises the real Berlin air-quality, Bright Sky/DWD and VBB endpoints through the complete refresh/publish/query path. Keeping this separate prevents transient third-party outages from making normal commit CI non-deterministic.

## Local development

Python agent example:

```bash
cd agents/air-quality-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=. pytest
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
pytest
```

Frontend:

```bash
cd frontend
npm install
npm test
npm run dev
```

The backend and repository abstractions retain local Turtle modes for deterministic tests and debugging, while the Compose runtime uses persistent Fuseki/TDB2 storage and direct remote SPARQL queries.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — runtime and semantic architecture
- [`docs/data-sources.md`](docs/data-sources.md) — public data sources and source constraints
- [`docs/analysis.md`](docs/analysis.md) — Urban Stress methodology and limitations
- [`docs/development.md`](docs/development.md) — incremental/TDD development strategy
- [`docs/decisions/`](docs/decisions/) — architectural decision records

## Relationship to The World Avatar

The design is inspired by architectural ideas used in The World Avatar: domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, persistent semantic storage and derived information. Berlin Urban Live Twin is an independent implementation for learning and software-engineering experimentation and does not copy The World Avatar source code.
