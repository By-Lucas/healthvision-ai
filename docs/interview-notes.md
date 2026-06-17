# Interview notes (simple English)

> A quick, plain-English script for talking about this project in an interview.
> Educational/portfolio project — not a medical diagnosis tool.

## What is this project?

HealthVision AI is a small but realistic HealthTech app. A user uploads a chest
X-ray image, the system analyzes it with AI in the background, and shows the
result (NORMAL / PNEUMONIA / UNCERTAIN) with a confidence score, a dashboard, and
a history. I built it to show how I design and ship full-stack software, not to
make a real diagnosis.

## How I used Python

I used **Python 3.11** with **FastAPI** for the API. I applied **Clean
Architecture**: the business logic (domain + use cases) is pure Python with no
framework imports, and the database, queue, storage and AI are "adapters" behind
interfaces called **ports**. This makes the code easy to test and easy to change.

## How I used React

The frontend is **React + TypeScript + Vite**, organized by **feature** (upload,
dashboard, history, detail). Each feature has its own components, hooks, services
and types. I used **React Query** for server data (caching and polling) and
**Zustand** for a little bit of global state. Styling is **TailwindCSS** and
charts use **Recharts**.

## How I used AI

The AI sits behind an interface (`AIInferenceService`). By default it runs a
**deterministic mock** so the whole pipeline works without downloading a big
dataset, but the output looks exactly like a real model (class + confidence +
probabilities). There's also a **PyTorch** engine ready to load real weights —
switching is just an environment variable, no code changes. I preprocess images
with OpenCV/Pillow and apply an "uncertainty gate" so the model says UNCERTAIN
instead of guessing.

## How I organized the frontend

Feature-sliced (modular) structure: every domain feature is self-contained, and
shared building blocks (UI components, the API client, types) live in `shared/`.
This keeps features independent and would make it easy to split into
micro-frontends later.

## How I organized the backend

Four layers: **domain** (entities, value objects, ports), **application** (use
cases), **infrastructure** (SQLAlchemy, Celery, storage, AI), and **interfaces**
(FastAPI routes + schemas). Dependencies only point inward. I wire the concrete
classes together in one place (the "composition root").

## How async processing works

When you upload an image, the API saves it, creates a record with status
PENDING, and puts a job on **RabbitMQ**. A **Celery** worker picks it up, runs
the AI, and updates the record to COMPLETED (or FAILED). The API responds
immediately, and the frontend polls until the result is ready. This keeps the app
responsive and lets me scale the workers separately from the API.

## How this could run on AWS

Because of the ports & adapters design, I'd swap adapters, not logic: **S3** for
images, **Aurora PostgreSQL** for the database, **Amazon MQ/SQS** for the queue,
**ECS/Fargate** for the API and worker, **ECR** for images, **CloudWatch** for
logs, and **S3 + CloudFront** for the frontend. (Details in
[cloud-aws.md](cloud-aws.md).)

## How I would improve this in production

- Train and ship a real model + add Grad-CAM heatmaps for explainability.
- Add authentication and per-user history (already stubbed).
- Add an S3 storage adapter and presigned upload URLs.
- Add observability: structured logs, metrics, tracing, alerts.
- Track model versions and evaluation metrics (precision/recall) on the dashboard.

## Three things I'm proud of

1. The AI is swappable (mock ↔ real) with **zero** changes to business code.
2. The backend tests run with **no external services** thanks to the ports.
3. It all runs with a single `make up`.
