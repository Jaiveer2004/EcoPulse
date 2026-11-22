# EcoPulse — Final Project Blueprint

EcoPulse is an environmental intelligence and monitoring platform built as a portfolio-quality data engineering project.

> **Scope:** Environmental data collection, large-scale processing, quality monitoring, anomaly detection, analytics, and an AI-powered knowledge assistant.

The project follows production-oriented engineering practices while clearly documenting the limitations of a portfolio-scale implementation. Reliability, security, testing, documentation, and operational practices are included, with deployment limitations documented separately.

---

## 1. Platform overview

EcoPulse models environmental monitoring stations across multiple cities.

Each station produces readings such as:

- PM2.5 and PM10 particulate concentrations.
- Temperature and humidity.
- Carbon monoxide, nitrogen dioxide, and other supported pollutant measurements.
- Station status and sensor health.
- Measurement timestamp and geographic location.

The platform also collects historical environmental data and weather information from external sources.

The platform supports analysis such as:

- How has PM2.5 changed in a particular city over the last 30 days?
- Which monitoring stations report the most inconsistent readings?
- Are there unusual pollution measurements?
- How does weather correlate with observed air-quality measurements?
- Which locations have insufficient or stale data?
- What do environmental guidelines say about a particular pollutant?

EcoPulse is designed to transform raw environmental information into useful, traceable, and well-documented insights through reliable data pipelines.

## Final deliverables

| Area | Scope |
| --- | --- |
| **Data Platform** | Ingestion, CDC, streaming, Spark, Delta Lake, medallion architecture. |
| **Analytics Platform** | Databricks SQL, dashboards, historical analysis and KPIs. |
| **ML Platform** | Anomaly detection, model evaluation and prediction experiments. |
| **AI Knowledge Assistant** | RAG over environmental reports and documented guidelines. |
| **Quality & Governance** | Validation, lineage, access control, provenance and auditability. |
| **Operations** | Orchestration, logging, monitoring, recovery and failure handling. |

---

## 2. Final technology stack

Each technology has a defined responsibility within the platform.

| Component               | Technology                 | Purpose                                         |
| ----------------------- | -------------------------- | ----------------------------------------------- |
| Primary source database | PostgreSQL                 | Stations, readings and source metadata          |
| Change Data Capture     | Debezium                   | Capture PostgreSQL inserts, updates and deletes |
| Event streaming         | Apache Kafka               | Transport environmental events                  |
| Connector management    | Kafka Connect              | Run Debezium connectors                         |
| Batch processing        | PySpark                    | Historical data processing                      |
| Stream processing       | Spark Structured Streaming | Process incoming events                         |
| Storage                 | Delta Lake                 | Reliable analytical tables                      |
| Local object storage    | MinIO                      | S3-compatible data lake storage                 |
| Analytics               | Databricks SQL             | Query Gold datasets and dashboards              |
| Orchestration           | Apache Airflow             | Schedule and coordinate pipelines               |
| ML                      | Spark MLlib                | Anomaly detection and prediction experiments    |
| AI/RAG                  | Python + LangChain         | Environmental knowledge assistant               |
| Vector storage          | PostgreSQL + pgvector      | Store and retrieve document embeddings          |
| API layer               | FastAPI                    | Serve application data and AI functionality     |
| Containerization        | Docker Compose             | Reproducible local infrastructure               |
| Testing                 | Pytest                     | Pipeline, data quality and integration tests    |
| Version control         | Git + GitHub               | Code management and collaboration               |

### Architecture decisions

- PostgreSQL is the operational database, not the analytical warehouse.
- Kafka transports events; it does not replace the data lake.
- Delta Lake holds analytical data in Bronze, Silver and Gold layers.
- Airflow coordinates batch workflows and does not orchestrate every streaming event.
- Databricks provides a cloud analytics environment, while local infrastructure remains the reproducible development environment.
- Open-source components are preferred wherever practical, without assuming paid cloud services are available.

## Hybrid environment: how local and Databricks will coexist

Local Spark and Databricks have distinct responsibilities rather than duplicating the same processing.

| Environment | Components and outputs |
| --- | --- |
| **Local development environment** | **Docker Compose:** PostgreSQL · Kafka · Debezium · MinIO · Spark · Airflow<br>**Local Delta Lake:** Bronze → Silver → Gold · Checkpoints · Data quality<br>Publish versioned analytical snapshots |
| **Databricks environment** | Import supported datasets · Databricks SQL · Dashboards · ML experiments |

The local environment runs the complete reproducible ingestion and processing stack. Databricks is used for cloud-side analytical exploration, SQL, dashboarding, and selected ML experiments.

A controlled publication mechanism will be established for Gold datasets. Initially, this can be a versioned Parquet export and import; the storage and ingestion options supported by the Databricks environment must be verified before selecting the final method.

A locally hosted Kafka cluster is not automatically reachable from a cloud Databricks workspace, so the platform does not depend on that connection.

This provides a functioning local platform and Databricks experience without requiring continuously running paid infrastructure.

---

## 3. Complete EcoPulse architecture

The following is the target architecture. Components can be implemented incrementally.

### EcoPulse — End-to-end architecture

| Area | Components and responsibilities |
| --- | --- |
| **Data sources** | Public environmental APIs · Historical datasets · Synthetic IoT sensors · Environmental documents |
| **Batch ingestion** | Python collectors · API extraction · File ingestion |
| **Streaming ingestion** | PostgreSQL · Debezium · Kafka |
| **Data lake — MinIO + Delta Lake** | **Bronze:** Raw<br>**Silver:** Clean<br>**Gold:** Business-ready |
| **Processing** | Spark batch + Structured Streaming · Data quality · Deduplication · Checkpoints |
| **Analytics & intelligence** | Databricks SQL · MLlib · RAG · Vector retrieval |
| **Application API** | **FastAPI:** Application API |
| **Dashboards** | Environmental insights |
| **EcoPulse AI Assistant** | Answers grounded in indexed environmental documents |

> **Cross-cutting:** Airflow orchestration · Pytest · Logging · Monitoring · Security · Governance · Lineage

### Data sources

The platform uses a combination of real public data and synthetic data.

| Source                              | Data                                 | Usage                                         |
| ----------------------------------- | ------------------------------------ | --------------------------------------------- |
| OpenAQ                              | Air-quality measurements             | Historical and available current observations |
| Open-Meteo                          | Weather observations and forecasts   | Weather context                               |
| Synthetic sensor generator          | PM2.5, PM10, temperature, humidity   | Continuous event streaming                    |
| PostgreSQL                          | Station registry and sensor metadata | Operational data and CDC                      |
| Official environmental publications | Reports and guidelines               | RAG knowledge base                            |

API access, licensing, attribution, coverage, and rate limits must be verified before integrating any external source. Synthetic measurements are always labelled as synthetic.

### Analytical data model

The initial Gold layer contains tables such as:

| Table                      | What it represents                |
| -------------------------- | --------------------------------- |
| `gold_air_quality_hourly`  | Hourly pollutant measurements     |
| `gold_air_quality_daily`   | Daily air-quality summaries       |
| `gold_city_comparison`     | City-level comparisons            |
| `gold_station_health`      | Station freshness and reliability |
| `gold_pollution_anomalies` | Detected unusual measurements     |
| `gold_weather_correlation` | Weather and air-quality analysis  |

These will be supported by Silver-level tables for stations, measurements, weather observations, and CDC-applied records.

Precise schemas and keys will be defined during implementation.

---

## 4. Failure testing and recovery

Controlled failure testing is part of the platform's reliability strategy.

Failures are introduced only in development environments and never by corrupting the only copy of the data.

Each failure exercise has four objectives:

1. Reproduce the failure.
2. Diagnose it using evidence.
3. Fix the root cause.
4. Add a safeguard to prevent recurrence or detect it sooner.

## Planned failure scenarios

The following scenarios are tested through controlled configuration changes or dedicated test scripts.

| Stage          | Failure scenario                     | Diagnostic focus                                     |
| -------------- | ------------------------------------ | --------------------------------------------------- |
| Infrastructure | Container fails to start             | Docker logs, health checks, networking              |
| PostgreSQL     | Invalid connection credentials       | Connection errors, configuration and secrets        |
| CDC            | Debezium connector fails             | Connector status, permissions, replication settings |
| Kafka          | Consumer reads duplicate events      | Delivery semantics, idempotency                     |
| Kafka          | Consumer falls behind                | Lag, throughput and partitioning                    |
| Ingestion      | API returns HTTP 429                 | Rate limiting, retries and backoff                  |
| Ingestion      | API response changes schema          | Schema validation and evolution                     |
| Spark          | Wrong column name                    | Analysis exceptions and schema inspection           |
| Spark          | Incompatible data types              | Casting and data validation                         |
| Streaming      | Checkpoint path is invalid           | Checkpoint recovery and state                       |
| Streaming      | Late-arriving records                | Event time and watermarks                           |
| Delta          | Duplicate keys during MERGE          | Deduplication and merge conditions                  |
| Data quality   | Missing and impossible readings      | Quarantine and quality rules                        |
| Orchestration  | Airflow task fails                   | Retries, dependencies and backfills                 |
| Databricks     | Incompatible file/schema assumptions | Import and schema compatibility                     |
| ML             | Data leakage                         | Correct train/test separation                       |
| RAG            | Incorrect document retrieval         | Chunking, metadata and retrieval evaluation         |
| API            | Missing environment variable         | Configuration validation and error handling         |

### Example failure workflow

For duplicate readings after a consumer restart, the investigation covers:

- The Kafka message.
- Its event identifier.
- The consumer offset.
- The Delta table records.
- The checkpoint location.

The root cause is identified from this evidence, followed by implementation of a deduplication and idempotency strategy. A regression test verifies that the same event cannot create duplicate analytical records.



### Reliability standard

> Every important failure should leave behind a test, validation rule, operational safeguard, or documented recovery procedure.



---

## 5. Implementation roadmap

Implementation is organized into ten stages. Each stage ends with a working deliverable and a verification exercise.

### EcoPulse implementation roadmap

10 stages · Sequential implementation

### Stage 0 — Project Foundation & Engineering Standards

- Define project scope and requirements.
- Create GitHub repository and folder structure.
- Establish Docker Compose environment.
- Configure environment variables and secrets.
- Define naming conventions, logging and error handling.
- Write the initial architecture and data-source documentation.

**Deliverable:** A reproducible development environment and professional project structure.

### Stage 1 — Infrastructure & Data Source Development
- Start PostgreSQL and MinIO.
- Create station and measurement schemas.
- Generate realistic synthetic sensor readings.
- Integrate an external environmental API.
- Build batch extraction scripts.
- Store raw files with source and ingestion metadata.

**Deliverable:** A functioning environmental data collection system.

### Stage 2 — CDC & Event Streaming
- Configure Kafka and Kafka Connect.
- Connect Debezium to PostgreSQL.
- Capture inserts, updates and deletes.
- Build a Kafka consumer for environmental events.
- Inspect message keys, payloads, offsets and partitions.
- Implement event identity and basic deduplication.

**Deliverable:** Operational database changes flowing into Kafka.

### Stage 3 — Spark & Delta Lake Processing
- Set up PySpark.
- Read historical files and streaming events.
- Implement Bronze, Silver and Gold.
- Apply transformations, aggregations and joins.
- Handle schema evolution, late data and duplicates.
- Implement Delta writes and MERGE operations.

**Deliverable:** A working medallion data lake.

### Stage 4 — Data Quality & Governance
- Implement completeness and validity checks.
- Add duplicate and freshness checks.
- Build quarantine tables.
- Track source information and processing metadata.
- Implement access restrictions and data retention rules.
- Add automated quality tests.

**Deliverable:** A trustworthy and auditable data platform.

### Stage 5 — Orchestration & Pipeline Reliability
- Integrate Airflow.
- Schedule batch ingestion and processing.
- Define task dependencies.
- Configure retries and failure notifications.
- Implement backfills and recovery.
- Monitor pipeline executions.

**Deliverable:** Automated and recoverable data workflows.

### Stage 6 — Databricks Analytics
- Set up the Databricks workspace.
- Publish Gold snapshots.
- Import and query analytical datasets.
- Build SQL queries and analytical views.
- Create dashboards and KPIs.
- Compare local Spark results with Databricks results.

**Deliverable:** A cloud analytics environment with verifiable results.

### Stage 7 — Machine Learning with Spark MLlib
- Prepare features from Gold data.
- Identify suitable anomaly-detection approaches.
- Build a baseline model.
- Train and evaluate a model.
- Examine data leakage and class imbalance.
- Store predictions and model evaluation results.

**Deliverable:** An evaluated environmental anomaly-detection experiment.

### Stage 8 — Environmental RAG Assistant
- Ingest environmental publications.
- Parse and clean documents.
- Implement chunking and embeddings.
- Store vectors in pgvector.
- Build retrieval and answer-generation workflows.
- Evaluate retrieval quality, grounding and citations.

**Deliverable:** A knowledge assistant that answers from documented sources.

### Stage 9 — Integration, Testing & Portfolio Release
- Build FastAPI endpoints.
- Integrate analytics and AI components.
- Add unit, integration and end-to-end tests.
- Review security, logging and observability.
- Prepare architecture diagrams and documentation.
- Record a demonstration and publish the GitHub repository.

**Deliverable:** The completed EcoPulse portfolio project.

---

## 6. Professional engineering standards

These standards apply from the first commit.

### Code quality

- Modular Python packages rather than one giant notebook.
- Type hints and meaningful function names.
- Configuration separated from application code.
- Centralized logging and structured error handling.
- No credentials committed to GitHub.
- Reusable ingestion and transformation functions.

### Data engineering standards

- Every source record should have traceable provenance.
- Every pipeline should be restartable wherever practical.
- Transformations should be repeatable and idempotent where required.
- Schema changes should be handled explicitly.
- Failed records should be recoverable.
- Data quality should be measurable.

### Testing standards

| Test type          | Verification scope                                |
| ------------------ | ------------------------------------------------- |
| Unit tests         | Individual transformations and utility functions  |
| Integration tests  | PostgreSQL, Kafka, Spark and storage interactions |
| Data quality tests | Nulls, duplicates, invalid values and freshness   |
| Pipeline tests     | End-to-end execution and recovery                 |
| Regression tests   | Previously fixed bugs do not return               |
| RAG evaluations    | Retrieval relevance and answer grounding          |

Pytest is the primary testing framework.

### Security standards

- Environment variables and `.env` files for local secrets.
- `.env.example` with placeholder values.
- Least-privilege database accounts.
- No personal information in synthetic sensor records.
- Dependency pinning and vulnerability checks.
- Documented retention and deletion policies.

---

## 7. Proposed GitHub repository structure

The structure evolves as the project develops; empty directories are not created in advance.

```
ecopulse/
│
├── ingestion/
│   ├── batch/
│   ├── api/
│   └── generators/
│
├── infrastructure/
│   ├── docker/
│   ├── postgres/
│   ├── kafka/
│   └── debezium/
│
├── streaming/
│   ├── producers/
│   └── consumers/
│
├── spark/
│   ├── batch/
│   ├── streaming/
│   └── transformations/
│
├── lakehouse/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── orchestration/
│   └── airflow/
│
├── databricks/
│   ├── notebooks/
│   └── sql/
│
├── ml/
│   ├── features/
│   ├── training/
│   └── evaluation/
│
├── rag/
│   ├── ingestion/
│   ├── retrieval/
│   └── evaluation/
│
├── api/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── end_to_end/
│
├── docs/
│   ├── architecture/
│   ├── decisions/
│   └── incidents/
│
├── scripts/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

The `incidents/` documentation records each major failure with:

1. Incident description.
2. Symptoms and error messages.
3. Root cause.
4. Resolution.
5. Prevention and monitoring.
6. Regression test reference.

Incident records provide a practical engineering history and support technical documentation.

---

## 8. Resource and cost strategy

The project is designed to remain affordable and reproducible.

The initial setup uses:

- Docker Compose for local infrastructure.
- Local MinIO storage.
- Local Spark for batch and streaming.
- Local Airflow.
- Databricks Free Edition for supported analytics and experimentation.
- Free public datasets and APIs, subject to their terms.
- A free-tier or local LLM/embedding option where practical.

The project avoids always-on cloud servers, paid managed Kafka, paid database hosting, and unnecessary AWS resources.

Kafka, Spark, Airflow, PostgreSQL and MinIO together can consume considerable RAM. Services should be built and started incrementally, with resource consumption measured before running them simultaneously.

---

## 9. Project completion criteria

Completion is measured through reproducible, testable outcomes rather than a demonstration alone.

### EcoPulse completion checklist

> **Progress**
>
> 0 of 15 completed
>
> 0%

- [ ] A fresh developer can reproduce the environment using documented setup steps.
- [ ] Batch ingestion works with real public or clearly labelled synthetic data.
- [ ] CDC changes flow from PostgreSQL through Debezium and Kafka.
- [ ] Spark processes both historical and streaming data.
- [ ] Bronze, Silver and Gold datasets are available.
- [ ] Duplicate and invalid records are handled correctly.
- [ ] Pipelines can recover from tested failures.
- [ ] Airflow orchestrates scheduled workflows.
- [ ] Databricks can query published Gold datasets.
- [ ] SQL dashboards display traceable analytical results.
- [ ] ML experiments include proper evaluation and limitations.
- [ ] RAG responses cite their supporting documents.
- [ ] FastAPI exposes documented application endpoints.
- [ ] Automated tests cover critical transformations and failure scenarios.
- [ ] GitHub contains architecture, setup, data dictionary and incident documentation.

---

## Current milestone

### Stage 0 / 10

#### Project Foundation & Engineering Standards

The initial milestone establishes the repository, development environment, configuration and logging conventions, and core infrastructure.

### First milestone deliverables

- GitHub repository initialized.
- Python project configured.
- Docker environment verified.
- PostgreSQL and MinIO running.
- Environment configuration secured.
- Initial README and architecture documentation.