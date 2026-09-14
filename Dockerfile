FROM python:3.12-slim

WORKDIR /app

COPY agents/air-quality-agent/requirements.txt /tmp/air-quality-requirements.txt
COPY agents/weather-agent/requirements.txt /tmp/weather-requirements.txt
COPY agents/transit-agent/requirements.txt /tmp/transit-requirements.txt
COPY agents/analysis-agent/requirements.txt /tmp/analysis-requirements.txt

RUN pip install --no-cache-dir \
    -r /tmp/air-quality-requirements.txt \
    -r /tmp/weather-requirements.txt \
    -r /tmp/transit-requirements.txt \
    -r /tmp/analysis-requirements.txt \
    "pyshacl>=0.30,<1.0"

COPY agents ./agents
COPY scripts ./scripts
COPY ontology ./ontology

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "scripts.refresh_all"]
