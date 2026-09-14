# Derived information: Urban Stress Index

## Purpose

The Urban Stress Index is an exploratory derived-information model used to demonstrate how observations from independent urban domains can be transformed into a new semantic quantity. It is not intended as a validated public-health, mobility, or policy indicator.

The present model combines three interpretable components:

- an air-quality component derived from an ordinal air-quality grade;
- a heat component derived from ambient temperature; and
- a transit component derived from the share of delayed public-transport trip updates.

## Normalisation

Each source quantity is transformed into the interval `[0, 1]` before weighting.

Air quality:

```text
A = clamp((grade - 1) / 5, 0, 1)
```

Heat:

```text
H = clamp((temperature_C - 20) / 15, 0, 1)
```

Transit disruption:

```text
T = clamp(delayed_share / 0.5, 0, 1)
```

The current composite index is:

```text
UrbanStress = 100 * (0.40 * A + 0.30 * H + 0.30 * T)
```

The weights and thresholds are deliberately explicit. This makes the derivation reproducible and allows later empirical calibration without changing the semantic integration architecture.

## Current status

The calculation and its RDF representation are implemented and covered by automated tests. The derived-information module is not yet connected to the live refresh pipeline because the shared graph currently contains air-quality station metadata but not live Berlin air-quality-index observations.

The model will only be integrated into the live pipeline after air-quality measurement ingestion has been implemented and tested. This prevents the demonstrator from presenting synthetic or manually supplied values as live city observations.

## Interpretation

A higher value represents a larger combined value of the three modelled stress components. The number must not be interpreted as a probability, health-risk estimate, or official Berlin indicator. It is an engineering demonstrator for cross-domain semantic derivation.
