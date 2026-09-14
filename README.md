# Berlin Urban Live Twin

An urban digital twin project that integrates real-world data to create a dynamic representation of Berlin and support cross-domain analysis of environmental, mobility, and infrastructure conditions.

## Project objective

The project explores how heterogeneous urban data can be progressively integrated into a common semantic representation. Rather than building a conventional dashboard that queries unrelated APIs directly, the system is developed around a knowledge-graph-oriented architecture in which domain agents ingest, normalise, and semantically describe urban observations.

The implementation is intentionally incremental. Each development stage introduces one architectural capability at a time so that design decisions and their evolution remain visible in the repository history.

## Current development stage

The first implemented domain is Berlin air quality. The current agent can:

- retrieve monitoring-station metadata from the official Berlin air-quality REST API;
- map external station payloads to an internal domain model;
- represent station metadata as RDF;
- merge RDF data into an in-memory knowledge graph; and
- retrieve active station identifiers using SPARQL.

Measurement ingestion, additional urban domains, persistent graph storage, analytical agents, APIs, visualisation, and containerisation are planned as later increments.

## Development approach

The project follows test-driven development where practical. New behaviour is first described by an automated test, followed by the smallest implementation required to satisfy that behaviour. Documentation evolves alongside the implementation.

## Repository structure

```text
agents/
  air-quality-agent/
    app/
    tests/
docs/
```

## Running the air-quality agent

From `agents/air-quality-agent`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m app.main
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Running tests

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest
```

## Data sources

Data-source notes are maintained in [`docs/data-sources.md`](docs/data-sources.md).
