# Berlin Urban Live Twin

An urban digital twin project that integrates real-world data to create a dynamic representation of Berlin and support cross-domain analysis of environmental, mobility, and infrastructure conditions.

## Project objective

Berlin Urban Live Twin explores how heterogeneous urban data can be integrated into a shared semantic representation rather than consumed independently by a conventional dashboard. Domain-specific agents retrieve external data, validate and normalise it into explicit internal models, and transform those models into RDF. The resulting semantic state can then be queried across domains and exposed through a common API and spatial user interface.

The project is intentionally developed in small increments. Tests, implementation, documentation, and infrastructure are introduced step by step so that the evolution of the design remains visible in the repository history.

## Current prototype

The prototype contains three live urban-data ingestion domains plus one derived-information agent:

- **Air quality:** active Berlin monitoring stations plus the official hourly Berlin Luftqualitätsindex (LQI).
- **Weather:** current Berlin weather observations through Bright Sky using open Deutscher Wetterdienst data.
- **Public transport:** official VBB GTFS-Realtime data reduced to a reproducible operational delay snapshot.
- **Urban stress analysis:** an explicit experimental 0-100 cross-domain index derived from current LQI, heat and transit disruption.

The refresh workflow updates all source domains, derives the Urban Stress observation, keeps inspectable Turtle exports, and publishes the integrated graph into a persistent Apache Jena Fuseki/TDB2 store. The FastAPI backend uses the Graph Store as its runtime source when configured, while retaining the file-backed mode for isolated tests and local debugging.

The frontend visualises current conditions, source freshness and station-level LQI information on a Berlin map.

## Architecture

```text
Berlin Air Quality API       DWD-derived Weather       VBB GTFS-Realtime
          |                         |                         |
          v                         v                         v
   Air Quality Agent          Weather Agent             Transit Agent
          |                         |                         |
          +------------ validation / domain models ----------+
                                    |
                                    v
                              RDF representation
                                    |
                             Turtle exports
                                    |
                                    v
                              Analysis Agent
                                    |
                           derived RDF observation
                                    |
                                    v
                         integrated RDF publication
                                    |
                                    v
                       Apache Jena Fuseki / TDB2
                         persistent Graph Store
                                    |
                                    v
                           RDFLib/SPARQL query layer
                                    |
                                    v
                             FastAPI backend
                                    |
                                    v
                         React / MapLibre frontend
```

## Experimental Urban Stress Index

The Urban Stress Index is intentionally transparent rather than predictive. It combines:

- 40% air-quality stress from the **worst current official Berlin LQI station grade**;
- 30% heat stress from the latest temperature observation; and
- 30% transit stress from the latest share of delayed VBB trip updates.

The analysis refuses to derive a value when the newest source observations are more than two hours apart. The result is written back as RDF so that the derivation remains inspectable and reproducible. It is an engineering experiment, not an official public-health or transport metric.

## Data freshness

Persisted data is not automatically treated as live. The backend exposes source-specific freshness states through `GET /freshness` using prototype thresholds:

- air quality: 2 hours;
- weather: 2 hours;
- transit: 15 minutes;
- derived Urban Stress: 2 hours.

Each source is classified as `fresh`, `stale`, or `missing`. The dashboard surfaces this status rather than silently presenting old observations as current.

## Development approach

The project follows test-driven development where practical. Behaviour is introduced using a Red-Green-Refactor cycle: tests describe the intended behaviour first, the smallest implementation is then added, and structural improvements follow without changing observable behaviour.

GitHub Actions validates the Python agent suites, semantic mappings, SPARQL-backed repository and API behaviour, orchestration and graph publication, frontend tests, TypeScript production build, Docker Compose configuration, and service-image builds.

See [`docs/development.md`](docs/development.md), [`docs/architecture.md`](docs/architecture.md), and [`docs/analysis.md`](docs/analysis.md).

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
docs/
scripts/
data/
docker-compose.yml
```

Each Python domain agent owns its client, validation/mapping logic, semantic mapping, tests, and runtime dependencies. This keeps external source schemas isolated from the shared semantic representation.

## Running the prototype

### 1. Build and start the persistent graph store

```bash
docker compose up -d fuseki
```

Fuseki is exposed at `http://localhost:3030`; the persistent dataset is published as `/twin` and stored in the Docker volume `fuseki-data`.

### 2. Refresh urban data, derive information, and publish RDF

```bash
docker compose run --rm refresh
```

The refresh process writes inspectable Turtle files into `data/`, derives `urban-stress.ttl`, merges the current semantic state, and replaces the Fuseki default graph through the SPARQL Graph Store Protocol.

### 3. Start API and frontend

```bash
docker compose up -d backend frontend
```

The API is available at `http://localhost:8000` and the frontend at `http://localhost:8080`.

Useful API endpoints include:

```text
GET /health
GET /state
GET /freshness
GET /stations
GET /air-quality
GET /weather
GET /transit
GET /urban-stress
GET /graph
```

Fuseki also exposes the persistent dataset at:

```text
http://localhost:3030/twin/sparql
http://localhost:3030/twin/data
```

## Local development

For an individual Python agent, create a virtual environment inside that agent directory and install its development requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=. pytest
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
pytest
```

Frontend development:

```bash
cd frontend
npm install
npm test
npm run dev
```

The backend defaults to local Turtle files when `TWIN_GRAPH_STORE_URL` is not set. This keeps unit/integration tests deterministic while the Docker runtime uses the persistent Graph Store.

## Semantic model

The project vocabulary is maintained in [`ontology/city.ttl`](ontology/city.ttl). RDF mappings use a small project-specific vocabulary together with established geographic predicates where appropriate. SPARQL is used to query the integrated state rather than exposing source-specific JSON structures directly to the presentation layer.

## Data sources

Source selection and integration details are documented in [`docs/data-sources.md`](docs/data-sources.md).

## Relationship to The World Avatar

The architecture is inspired by concepts used in The World Avatar, including domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, persistent semantic storage, and derived information. Berlin Urban Live Twin is an independent implementation intended for learning, experimentation, and software-engineering practice; it does not copy The World Avatar source code.
