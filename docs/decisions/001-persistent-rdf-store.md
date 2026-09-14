# ADR 001: Persistent RDF storage with Apache Jena Fuseki/TDB2

## Status

Accepted

## Context

The first increments persisted each domain as Turtle and reconstructed an RDFLib graph in the backend. That approach kept the semantic model inspectable and made early tests simple, but it required whole-graph materialisation and did not provide a durable multi-process knowledge-graph service.

## Decision

Use Apache Jena Fuseki with a TDB2 dataset as the persistent runtime knowledge graph.

The refresh pipeline keeps Turtle exports for inspection, merges and validates the current state, then replaces the Fuseki default graph through the SPARQL Graph Store Protocol. Runtime API reads execute directly against `/twin/sparql`. Local-file and Graph-Store repository modes remain available for deterministic tests and compatibility.

## Consequences

The runtime has a real persistent RDF store and standard SPARQL interface. Backend queries scale independently of complete graph export size. The system gains another service dependency, so Docker health checks and container integration tests are required. Turtle remains useful for debugging but is no longer the operational source of truth in the Compose runtime.
