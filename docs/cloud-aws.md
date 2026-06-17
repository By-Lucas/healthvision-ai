# Cloud-ready architecture (AWS)

> Educational/portfolio project. Not a medical diagnosis tool.

HealthVision AI is built so that **going to the cloud means swapping adapters,
not rewriting logic** — a direct payoff of the ports & adapters design.

## Local vs AWS mapping

| Concern            | Local (this repo)            | AWS                                              |
|--------------------|------------------------------|--------------------------------------------------|
| Image storage      | `LocalFileStorage` → disk    | **S3** via an `S3Storage` adapter (same port)    |
| Relational DB      | PostgreSQL container         | **Aurora PostgreSQL (Serverless v2)**            |
| Message broker     | RabbitMQ container           | **Amazon MQ for RabbitMQ** or **SQS**            |
| Async worker       | Celery container             | **ECS/Fargate** task, or **Lambda** for spiky load |
| API                | Uvicorn container            | **ECS/Fargate** behind an **ALB**                |
| Container registry | local Docker                 | **ECR**                                          |
| Logs               | stdout                       | **CloudWatch Logs**                              |
| Frontend           | nginx container              | **S3 + CloudFront** (static + CDN)               |
| Secrets/config     | `.env`                       | **SSM Parameter Store / Secrets Manager**        |

## Target topology

```
                         ┌────────────── CloudFront (CDN) ──────────────┐
        Users ──────────▶│  static SPA from S3                          │
                         └───────────────────────┬──────────────────────┘
                                                  │ /api, /uploads
                                                  ▼
                                        Application Load Balancer
                                                  │
                                   ┌──────────────┴──────────────┐
                                   ▼                              ▼
                        ECS/Fargate: FastAPI            (auto-scaling group)
                                   │
            ┌──────────────────────┼───────────────────────────────┐
            ▼                      ▼                                 ▼
   Aurora PostgreSQL      Amazon MQ / SQS  ──tasks──▶  ECS/Fargate: Celery worker
     (Serverless v2)                                          │
            ▲                                                  ▼
            └──────────────── results ◀───────────  S3 (X-ray images)
                                                              │
                              all services ──▶ CloudWatch Logs / Metrics
                              images pulled from ──▶ ECR
```

## What changes in the code

Only **one new adapter** is needed for the storage swap, e.g.:

```python
class S3Storage(FileStorage):
    def __init__(self, bucket: str): ...
    def save(self, stored_filename, data) -> str: ...   # put_object, return s3:// or CDN URL
    def read(self, stored_filename) -> bytes: ...        # get_object
    def exists(self, stored_filename) -> bool: ...
```

Then bind it in the composition root (`dependencies.py` + the Celery task). The
`image_path` already stored on `Analysis` becomes a CloudFront/S3 URL, which the
frontend renders without changes.

If moving from RabbitMQ to SQS, Celery supports SQS as a broker — only
`CELERY_BROKER_URL` changes.

## Deployment pipeline (suggested)

1. GitHub Actions builds & tests (already in this repo).
2. On `main`, build images and push to **ECR**.
3. Update **ECS** services (API + worker) via a rolling deploy.
4. Run `alembic upgrade head` as a one-off ECS task / migration step.
5. Sync the built SPA to the **S3** bucket and invalidate **CloudFront**.

## Scaling & ops notes

- **API** and **worker** scale independently — bursty inference load doesn't
  degrade API latency.
- **Aurora Serverless v2** scales DB capacity with demand.
- **CloudWatch** centralizes logs (the app already logs to stdout in a structured
  format) and powers alarms/auto-scaling.
- For GPU inference, the worker task definition can target GPU-backed ECS
  capacity or SageMaker endpoints.
