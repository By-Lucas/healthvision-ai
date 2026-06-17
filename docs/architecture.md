# Architecture

> Educational/portfolio project. Not a medical diagnosis tool.

This document explains the architectural decisions behind HealthVision AI and
why they map to how real HealthTech systems are built.

## 1. Clean Architecture

The backend is organized in concentric layers where **dependencies only point
inward**:

```
┌─────────────────────────────────────────────┐
│ interfaces/   FastAPI routes, Pydantic schemas │  frameworks & drivers
│ ┌───────────────────────────────────────────┐ │
│ │ application/   use cases, DTOs              │ │  application business rules
│ │ ┌───────────────────────────────────────┐ │ │
│ │ │ domain/   entities, value objects,    │ │ │  enterprise business rules
│ │ │           services, PORTS             │ │ │  (pure Python, no deps)
│ │ └───────────────────────────────────────┘ │ │
│ └───────────────────────────────────────────┘ │
│ infrastructure/   DB, AI, storage, queue        │  adapters (implement ports)
└─────────────────────────────────────────────┘
```

- **domain** — `Analysis`, `User`, `Prediction` value object, validation &
  inference service abstractions, and the **ports** (`AnalysisRepository`,
  `FileStorage`, `AIInferenceService`). No imports from FastAPI/SQLAlchemy/torch.
- **application** — use cases that orchestrate the domain: `UploadExamImage`,
  `ProcessExamAnalysis`, `ListAnalysisHistory`, `GetAnalysisDetail`,
  `GetDashboardSummary`. They depend only on ports.
- **infrastructure** — concrete adapters: SQLAlchemy repository, local/S3
  storage, Celery queue, mock/PyTorch inference engines.
- **interfaces** — HTTP delivery mechanism (routes + schemas + DI wiring).

**Why:** business rules become testable in isolation and survive technology
changes. Swapping Postgres, RabbitMQ or the ML framework does not touch a use
case.

## 2. Hexagonal Architecture (Ports & Adapters)

The ports are the hexagon's edges:

| Port (domain)           | Adapter (infrastructure)              | Test double            |
|-------------------------|---------------------------------------|------------------------|
| `AnalysisRepository`    | `SqlAlchemyAnalysisRepository`        | `InMemoryAnalysisRepository` |
| `FileStorage`           | `LocalFileStorage` (→ `S3Storage`)    | `InMemoryStorage`      |
| `AIInferenceService`    | `MockInferenceEngine` / `TorchInferenceEngine` | `MockInferenceEngine` |

The **composition root** lives in `interfaces/api/dependencies.py` (for HTTP) and
in the Celery task (for async work) — the only places that know which concrete
adapter is bound to which port.

## 3. Light DDD

- **Entity** — `Analysis` has identity (`id`) and a lifecycle expressed as
  behavior (`mark_processing`, `complete`, `fail`), so invalid state transitions
  can't be expressed.
- **Value object** — `Prediction` is immutable and validated on construction
  (confidence in `[0,1]`); it also owns the plain-language `explanation()`.
- **Aggregate** — `Analysis` is the aggregate root persisted by the repository.
- **Domain service** — `ImageValidationService` holds rules that don't belong to
  a single entity.

We keep it *light*: no over-engineered bounded contexts for a single-aggregate
demo.

## 4. Flow: upload

1. `POST /api/v1/analysis/upload` → `UploadExamImageUseCase`.
2. `ImageValidationService` checks extension, content-type, size, and that the
   bytes decode as a real image (Pillow).
3. `FileStorage.save()` persists the bytes; `AnalysisRepository.add()` inserts a
   `PENDING` record.
4. `enqueue_analysis(id)` dispatches a Celery task and returns `201` immediately.

## 5. Flow: async processing

1. The Celery worker receives the task (`analysis.process`).
2. `ProcessExamAnalysisUseCase` loads the analysis, sets `PROCESSING`.
3. `FileStorage.read()` → `AIInferenceService.predict()` → `Prediction`.
4. `Analysis.complete(prediction)` or `Analysis.fail(error)`; the repository
   persists the new state.
5. The frontend polls `GET /analysis/{id}` until `COMPLETED`/`FAILED`.

## 6. Separation of responsibilities

- ORM models (`infrastructure/database/models`) ≠ domain entities. The repository
  maps between them, so the DB schema and the domain can evolve independently.
- Pydantic schemas (`interfaces/api/schemas`) ≠ entities. The API contract is
  explicit and decoupled from internals.
- Inference is hidden behind a port; the rest of the app never imports torch.

## 7. Why Celery + RabbitMQ

ML inference can be slow and bursty. Doing it inside the request would block the
client, couple API latency to model latency, and lose work on crashes. A broker
(RabbitMQ) + worker (Celery) gives us:

- **Responsiveness** — the API returns `PENDING` instantly.
- **Scalability** — scale workers independently of the API.
- **Resilience** — tasks are durable and retried on failure.

This mirrors real HealthTech pipelines (DICOM/image processing, OCR, report
generation) which are almost always asynchronous.

## 8. Why a modular React frontend

Each feature is a self-contained slice (`components/`, `hooks/`, `services/`,
`types/`, `pages/`). Benefits:

- **High cohesion, low coupling** — a feature can change without rippling out.
- **Micro-frontend ready** — a slice could be extracted to its own deployable
  with minimal effort.
- **Onboarding** — the folder structure documents the product's capabilities.

Server state lives in **React Query** (caching, polling, invalidation); only
genuinely global UI state lives in **Zustand**.

## 9. Relation to real HealthTech systems

| This project                         | Real-world analogue                          |
|--------------------------------------|----------------------------------------------|
| Image upload + validation            | DICOM/scan ingestion with integrity checks   |
| Async Celery inference               | GPU inference workers / batch pipelines      |
| Auditable `Analysis` records         | Regulated, traceable result storage          |
| Educational disclaimer everywhere    | Regulatory / clinical-safety guardrails      |
| Ports & adapters                     | Cloud portability, vendor independence       |

See also: [ai-model.md](ai-model.md) · [cloud-aws.md](cloud-aws.md) ·
[interview-notes.md](interview-notes.md).
