# v1 scope and known limitations

Berlin Urban Live Twin v1 is a software-engineering and semantic-integration reference implementation. It is deliberately narrower than a production municipal digital-twin platform.

## Data coverage

Air quality currently uses the official Berlin LQI rather than storing raw pollutant concentration time series. Weather is represented by a current Berlin reference observation rather than a city-wide meteorological grid. Transit is an aggregate snapshot of GTFS-Realtime trip updates and does not model individual routes, stops or passenger flows in the knowledge graph.

## Derived Urban Stress Index

Urban Stress is an explicit engineering demonstrator. Its weights and normalisation thresholds are not empirically calibrated and it must not be interpreted as a health-risk, public-safety, mobility-performance or policy indicator.

## Persistence model

Each refresh replaces the current default graph. The persistent store therefore represents current state, not a complete historical event log. Historical temporal modelling, named graphs and incremental graph updates are suitable future extensions.

## Availability

The system depends on public third-party data sources. The deterministic CI suite does not call those services. A separate scheduled live-source smoke test detects upstream schema or availability changes without making normal commit CI unreliable.

## Security and deployment

The Docker Compose configuration is intended for local development and portfolio demonstration. Fuseki and FastAPI are not configured with production authentication, TLS termination, network policies, rate limiting or secret-management infrastructure. Those concerns belong at a deployment/platform layer and should be added before exposing the stack on a public network.

## Semantic namespace

The project vocabulary currently uses a project-local example namespace. Before publishing the ontology as a long-lived shared vocabulary, the namespace should be moved to a stable, dereferenceable project URI with explicit versioning and governance.

## Validation

SHACL protects the graph contract that v1 depends on, but it cannot prove that an upstream observation is factually correct. It validates structure, datatypes and selected value ranges; source quality and completeness remain properties of the external datasets.
