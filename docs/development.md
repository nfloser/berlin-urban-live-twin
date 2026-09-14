# Development approach

## Incremental delivery

The repository is intentionally developed as a sequence of small vertical increments. The objective is to keep architectural decisions observable in the commit history rather than introducing the entire target architecture in a single initial implementation.

The current development sequence is:

1. air-quality station acquisition and validation;
2. semantic station representation with RDF and SPARQL;
3. weather ingestion as a second independent domain;
4. public-transport realtime ingestion through GTFS-Realtime;
5. transparent cross-domain derived-information logic;
6. a query API over the integrated RDF state;
7. a browser-based spatial visualisation; and
8. reproducible containerised execution.

## Test-driven development

Behavioural changes are introduced using a Red-Green-Refactor cycle where practical:

1. **Red:** write an automated test describing the intended behaviour;
2. **Green:** implement the smallest change that satisfies that behaviour; and
3. **Refactor:** improve structure without changing externally observable behaviour.

The repository history therefore deliberately contains commits in which a test is added before the corresponding implementation. Infrastructure-only changes may not always have a meaningful unit-test-first representation; these are validated through continuous integration and build checks instead.

## Continuous integration

GitHub Actions executes the independent Python test suites for each domain agent, the backend API tests, orchestration tests, frontend unit tests, and frontend production build checks. This keeps agent boundaries explicit and prevents Python packages with the same local `app` package name from leaking state into each other during tests.

## Data-source boundaries

External payloads are kept at the system boundary. Domain-specific clients retrieve source data, mapping functions normalise it into internal models, and RDF conversion occurs only after validation. This prevents source-specific JSON or Protocol Buffer schemas from becoming the internal representation of the digital twin.
