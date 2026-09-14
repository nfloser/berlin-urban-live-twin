# Derived information: Urban Stress Index

## Purpose

The Urban Stress Index is an exploratory derived-information model used to demonstrate how observations from independent urban domains can be transformed into a new semantic quantity. It is not intended as a validated public-health, mobility, or policy indicator.

The live model combines three interpretable components:

- an air-quality component derived from the worst current official Berlin LQI station grade;
- a heat component derived from the latest Berlin temperature observation; and
- a transit component derived from the latest share of delayed VBB trip updates.

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

## Temporal consistency

A cross-domain value is only generated when the latest LQI, weather, and transit source observations are sufficiently aligned in time. The current prototype permits a maximum spread of two hours between the oldest and newest source timestamps. If that condition is violated, the analysis agent raises an error instead of publishing a misleading mixed-age observation.

This rule is separate from absolute freshness. A later iteration can additionally compare all source timestamps with wall-clock time and expose a formal freshness status through the API.

## Live pipeline

The analysis module is now part of the top-level refresh workflow. The sequence is:

```text
Air quality + LQI -> air-quality.ttl
Weather           -> weather.ttl
VBB realtime      -> transit.ttl
                         |
                         v
                  Analysis agent
                         |
                         v
                  urban-stress.ttl
```

The derived observation is represented as RDF with its source-time-aligned observation timestamp and component values. The FastAPI backend exposes the latest result through `GET /urban-stress`.

## Interpretation

A higher value represents a larger combined value of the three modelled stress components. The number must not be interpreted as a probability, health-risk estimate, or official Berlin indicator. It is an engineering demonstrator for cross-domain semantic derivation.
