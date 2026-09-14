# Architecture

## Architectural goal

Berlin Urban Live Twin is developed as an incremental, knowledge-graph-oriented urban digital twin. External data sources are not exposed directly to the presentation layer. Each domain is instead handled by an ingestion agent that retrieves external data, converts it into an internal domain representation, maps that representation to RDF, and updates the shared semantic state.

```text
External urban data
        |
        v
Domain-specific client
        |
        v
Normalisation / validation
        |
        v
Domain model
        |
        v
RDF mapping
        |
        v
Knowledge graph
        |
        +-------------------+
        |                   |
        v                   v
SPARQL queries        Analytical agents
                            |
                            v
                    Derived information
```

## Current implementation

The first vertical slice implements Berlin air-quality station ingestion. It deliberately uses an in-memory RDFLib graph before introducing persistent graph infrastructure. This keeps the first development stages focused on semantic modelling and query behaviour rather than deployment concerns.

## Design principles

1. **External schemas remain at the boundary.** API payloads are mapped into explicit internal models before semantic conversion.
2. **Semantic representation is a first-class concern.** RDF is produced from domain objects rather than directly from arbitrary JSON.
3. **Derived information should be reproducible.** Analytical outputs will be modelled as data that can be written back into the graph.
4. **Infrastructure is introduced only when required.** The project starts locally and will later move to persistent graph storage and containerised services.
5. **Development is test-driven.** Behaviour is specified through automated tests before implementation where practical.

## Relationship to The World Avatar

The project is inspired by the architectural ideas used by The World Avatar: domain-oriented agents, semantic interoperability, knowledge graphs, SPARQL-based access, and derived information. It is an independent implementation designed for learning and experimentation rather than a copy of The World Avatar codebase.
