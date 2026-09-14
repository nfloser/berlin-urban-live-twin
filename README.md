# Berlin Urban Live Twin

An urban digital twin project that integrates real-world data to create a dynamic representation of Berlin and support cross-domain analysis of environmental, mobility, and infrastructure conditions.

## Project objective

Berlin Urban Live Twin explores how heterogeneous urban data can be integrated into a shared semantic representation rather than consumed independently by a conventional dashboard. Domain-specific agents retrieve external data, validate and normalise it into explicit internal models, and transform those models into RDF. The resulting semantic state can then be queried across domains and exposed through a common API and spatial user interface.

The project is intentionally developed in small increments. Tests, implementation, documentation, and infrastructure are introduced step by step so that the evolution of the design remains visible in the repository history.

## Current prototype

The current prototype contains three independent urban-data ingestion domains:

- **Air quality:** retrieves geolocated monitoring-station metadata from the official Berlin air-quality API and represents the stations as RDF.
- **Weather:** retrieves current Berlin weather observations from Bright Sky, based on open Deutscher Wetterdienst data, and maps them into the shared semantic model.
- **Public transport:** consumes the official VBB GTFS-Realtime feed, derives an aggregated delay snapshot, and represents that state as RDF.

The resulting Turtle files form an interim persisted semantic state. A FastAPI backend loads the RDF data and uses SPARQL queries to expose station, weather, transit, graph, and system-state endpoints. A React/MapLibre frontend visualises the current state and the spatial distribution of active air-quality monitoring stations.

An experimental analysis module also implements a transparent cross-domain **Urban Stress Index**. It is currently tested as an independent derived-information component and is not yet part of the live refresh pipeline because live air-quality-index measurements have not yet been integrated. The next air-quality increment will add measurement/LQI ingestion before this derived-information workflow is connected to the shared graph.

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
                                    v
                         shared semantic state
                              (Turtle / RDFLib)
                                    |
                              SPARQL queries
                                    |
                         +----------+----------+
                         |                     |
                         v                     v
                    FastAPI API         Analysis modules
                         |
                         v
                 React / MapLibre UI
```

The file-backed RDF state is intentionally an intermediate architecture. A persistent graph database is a later infrastructure step once the semantic model and agent boundaries are sufficiently stable.

## Development approach

The project follows test-driven development where practical. Behaviour is introduced using a Red-Green-Refactor cycle: tests describe the intended behaviour first, the smallest implementation is then added, and structural improvements follow without changing observable behaviour.

GitHub Actions validates the Python agent suites, SPARQL-backed repository and API behaviour, orchestration scripts, frontend tests, TypeScript production build, and container configuration/builds.

See [`docs/development.md`](docs/development.md) for the development strategy and [`docs/architecture.md`](docs/architecture.md) for architectural details.

## Repository structure

```text
agents/
  air-quality-agent/
  weather-agent/
  transit-agent/
  analysis-agent/
backend/
frontend/
ontology/
docs/
scripts/
data/
docker-compose.yml
```

Each Python domain agent owns its client, validation/mapping logic, semantic mapping, tests, and runtime dependencies. This keeps external source schemas isolated from the shared semantic representation.

## Running the prototype

### 1. Refresh urban data

The top-level refresh script executes the air-quality, weather, and transit agents sequentially and writes their RDF output to `data/`.

Each agent has its own Python dependencies. The easiest reproducible execution path is the refresh container:

```bash
docker compose run --rm refresh
```

### 2. Start API and frontend

```bash
docker compose up backend frontend
```

The API is available at `http://localhost:8000` and the frontend at `http://localhost:8080`.

Useful API endpoints include:

```text
GET /health
GET /state
GET /stations
GET /weather
GET /transit
GET /graph
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

## Semantic model

The initial project vocabulary is maintained in [`ontology/city.ttl`](ontology/city.ttl). RDF mappings use a small project-specific vocabulary together with established geographic predicates where appropriate. SPARQL is used to query the integrated state rather than exposing source-specific JSON structures directly to the presentation layer.

## Data sources

Source selection and current integration status are documented in [`docs/data-sources.md`](docs/data-sources.md).

## Relationship to The World Avatar

The architecture is inspired by concepts used in The World Avatar, including domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, and derived information. Berlin Urban Live Twin is an independent implementation intended for learning, experimentation, and software-engineering practice; it does not copy The World Avatar source code.
