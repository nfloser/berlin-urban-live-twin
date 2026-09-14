# Berlin Urban Live Twin

An urban digital twin project that integrates real-world data to create a dynamic representation of Berlin and support cross-domain analysis of environmental, mobility, and infrastructure conditions.

## Project objective

Berlin Urban Live Twin explores how heterogeneous urban data can be integrated into a shared semantic representation rather than consumed independently by a conventional dashboard. Domain-specific agents retrieve external data, validate and normalise it into explicit internal models, and transform those models into RDF. The resulting semantic state can then be queried across domains and exposed through a common API and spatial user interface.

The project is intentionally developed in small increments. Tests, implementation, documentation, and infrastructure are introduced step by step so that the evolution of the design remains visible in the repository history.

## Current prototype

The current prototype contains three live urban-data ingestion domains plus one derived-information agent:

- **Air quality:** retrieves active Berlin monitoring stations and the official, hourly Berlin Luftqualitätsindex (LQI) through the Berlin air-quality REST API. Station and LQI observations are represented separately in RDF and linked semantically.
- **Weather:** retrieves current Berlin weather observations from Bright Sky, based on open Deutscher Wetterdienst data, and maps them into the shared semantic model.
- **Public transport:** consumes the official VBB GTFS-Realtime feed, derives an aggregated delay snapshot, and represents that state as RDF.
- **Urban stress analysis:** reads the persisted RDF outputs of the three source domains and derives an explicitly weighted experimental 0-100 Urban Stress Index.

The central refresh workflow runs all source agents first and then the analysis agent. The resulting Turtle files form the persisted semantic state. A FastAPI backend loads these RDF files and uses SPARQL queries to expose station, LQI, weather, transit, derived-stress, graph, and system-state endpoints. A React/MapLibre frontend visualises the live cross-domain state and active monitoring stations.

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
                    +---------------+---------------+
                    |                               |
                    v                               v
              SPARQL / FastAPI              Analysis Agent
                    |                               |
                    |                     derived RDF observation
                    +---------------+---------------+
                                    |
                                    v
                         React / MapLibre UI
```

The file-backed RDF state is intentionally an intermediate architecture. A persistent graph database is a later infrastructure step once the semantic model and agent boundaries are sufficiently stable.

## Experimental Urban Stress Index

The prototype's Urban Stress Index is intentionally transparent rather than predictive. It combines:

- 40% air-quality stress from the **worst current official Berlin LQI station grade**;
- 30% heat stress from the latest temperature observation; and
- 30% transit stress from the latest share of delayed VBB trip updates.

The result is written back as RDF so that derived information remains inspectable and reproducible. It is an engineering experiment, not an official public-health or transport metric.

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

### 1. Refresh urban data and derived information

```bash
docker compose run --rm refresh
```

This updates air-quality/LQI, weather and transit RDF before deriving `urban-stress.ttl` from that shared state.

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
GET /air-quality
GET /weather
GET /transit
GET /urban-stress
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

The project vocabulary is maintained in [`ontology/city.ttl`](ontology/city.ttl). RDF mappings use a small project-specific vocabulary together with established geographic predicates where appropriate. SPARQL is used to query the integrated state rather than exposing source-specific JSON structures directly to the presentation layer.

## Data sources

Source selection and current integration status are documented in [`docs/data-sources.md`](docs/data-sources.md).

## Relationship to The World Avatar

The architecture is inspired by concepts used in The World Avatar, including domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, and derived information. Berlin Urban Live Twin is an independent implementation intended for learning, experimentation, and software-engineering practice; it does not copy The World Avatar source code.
