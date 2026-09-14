# ADR 002: Validate semantic state and retain source provenance

## Status

Accepted

## Context

A knowledge graph can be syntactically valid RDF while still violating application assumptions. Missing timestamps, impossible coordinate ranges, invalid LQI grades or unbounded derived values would make later SPARQL results unreliable. In addition, a digital twin should make the origin of observations inspectable rather than relying on documentation outside the graph.

## Decision

Use SHACL as a publication gate for the integrated graph and W3C PROV-O for source lineage.

`ontology/shapes.ttl` defines constraints for station, LQI, weather, transit and Urban Stress nodes. The refresh pipeline validates the complete integrated state after derivation and before persistent publication. A failed validation aborts publication, leaving the previously published graph intact.

Source observations use `prov:wasDerivedFrom`; weather also records DWD as its primary upstream source. The derived Urban Stress observation records all three external source datasets used by the current derivation. The backend exposes aggregated graph lineage through `GET /provenance`.

## Consequences

Semantic contract violations are detected before they enter the runtime knowledge graph. Provenance becomes queryable data rather than prose-only documentation. Refreshes can fail when upstream data violates the contract, which is intentional and is surfaced by the separate live-source smoke workflow.
