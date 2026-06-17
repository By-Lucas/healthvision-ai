<div align="center">

# 🩻 HealthVision AI

### Análise de raio-X de tórax com IA, construída como software de produção.

Demonstração full-stack de **HealthTech**: envie um raio-X de tórax → um
**pipeline assíncrono de IA** classifica (`NORMAL` / `PNEUMONIA` / `UNCERTAIN`)
com score de confiança, explicação simples, todos os achados por patologia,
dashboard e histórico.

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](backend)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](frontend)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](frontend)
[![PyTorch](https://img.shields.io/badge/PyTorch-torchxrayvision-EE4C2C?logo=pytorch&logoColor=white)](docs/ai-model.md)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](docker-compose.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Arquitetura:** Clean + Hexagonal + DDD leve · **Assíncrono:** Celery + RabbitMQ ·
**Testes:** Pytest · Vitest · Playwright

🇺🇸 [**English version**](README.md) · 🇧🇷 Português (você está aqui)

</div>

> ⚠️ **Aviso:** Este projeto é apenas para **fins educacionais e de portfólio.
> Não é uma ferramenta de diagnóstico médico.** Não use para decisões clínicas.

---

## Sumário

- [Visão geral](#visão-geral)
- [Problema resolvido & motivação](#problema-resolvido--motivação)
- [Stack de tecnologias](#stack-de-tecnologias)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Pipeline de IA](#pipeline-de-ia)
- [Fluxo de dados](#fluxo-de-dados)
- [Endpoints da API](#endpoints-da-api)
- [Como executar localmente](#como-executar-localmente)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Arquitetura cloud-ready (AWS)](#arquitetura-cloud-ready-aws)
- [Melhorias futuras](#melhorias-futuras)
- [Aviso legal](#aviso-legal)

---

## Visão geral

O usuário envia uma imagem de raio-X de tórax. A API valida, armazena, cria um
registro `Analysis` com status `PENDING` e despacha uma tarefa assíncrona para um
worker **Celery** via **RabbitMQ**. O worker executa o pipeline de IA
(pré-processamento → inferência), persiste o resultado, e o frontend faz polling
até a análise ficar `COMPLETED`. Os resultados alimentam um dashboard com
gráficos e um histórico filtrável.

O objetivo do projeto é demonstrar **maturidade de engenharia**, não acurácia
médica: mostra arquitetura Clean/Hexagonal, DDD leve, processamento assíncrono,
contratos tipados ponta a ponta, testes, Docker e CI/CD.

## Problema resolvido & motivação

Produtos reais de HealthTech compartilham um formato recorrente: ingerir
artefatos médicos, processá-los de forma assíncrona com ML, persistir resultados
auditáveis e exibi-los em dashboards — mantendo ML, infraestrutura e regras de
negócio desacoplados e testáveis.

Este repositório é uma reprodução compacta e honesta desse formato, com o intuito
de:

- demonstrar **arquitetura de backend de nível profissional** (Clean + Hexagonal + DDD leve);
- demonstrar um **frontend React modular** organizado por domínio;
- mostrar um **pipeline de ML assíncrono real** capaz de trocar o mock por um
  modelo real sem alterar a lógica de negócio;
- ser **totalmente executável** com um único `make up`.

## Stack de tecnologias

| Camada      | Tecnologias |
|-------------|-------------|
| Backend     | Python 3.11, FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, Celery, RabbitMQ |
| IA / dados  | Preditor pronto para PyTorch, OpenCV, Pillow, NumPy, Pandas, scikit-learn |
| Frontend    | React 18, TypeScript, Vite, React Query, Zustand, React Router, TailwindCSS, Recharts |
| Testes      | Pytest, Vitest, Testing Library, Playwright |
| DevOps      | Docker, Docker Compose, GitHub Actions, Makefile |

## Funcionalidades

1. **Início** — explicação do projeto, aviso educacional, botão de ação, resumo
   das tecnologias.
2. **Upload** — arrastar e soltar, validação no cliente e no servidor (tipo/tamanho),
   preview ao vivo, cria uma análise `PENDING`.
3. **Processamento assíncrono** — a FastAPI salva a imagem + registro no banco e
   enfileira a tarefa Celery; o worker executa a inferência e salva o resultado.
4. **IA** — um **motor mock** determinístico por padrão, com um motor **PyTorch**
   pronto para receber pesos reais. Classes: `NORMAL`, `PNEUMONIA`, `UNCERTAIN`.
5. **Resultado** — status, classe prevista, confiança, tempo de processamento,
   explicação, aviso educacional.
6. **Dashboard** — totais, distribuição por classe e por status, confiança média,
   gráfico de distribuição, análises recentes.
7. **Histórico** — lista com filtros por status/classe, links para o detalhe.
8. **Detalhe** — imagem, resultado, barra de confiança, explicação, metadados,
   atualização de status ao vivo (polling).

## Arquitetura

O backend segue **Clean Architecture + Hexagonal (Ports & Adapters) + DDD leve**.
As dependências sempre apontam para dentro; o domínio não conhece FastAPI,
SQLAlchemy, Celery ou PyTorch.

```
interfaces (rotas FastAPI, schemas)        ← adaptador mais externo
        │ depende de
application (casos de uso, DTOs)
        │ depende de
domain (entidades, value objects, serviços, PORTAS)   ← núcleo puro
        ▲ implementado por
infrastructure (repo SQLAlchemy, motores de IA, storage, Celery)  ← adaptadores
```

Portas principais (`backend/app/domain/`): `AnalysisRepository`, `FileStorage`,
`AIInferenceService`. Cada uma tem um adaptador concreto em `infrastructure/` e
um fake em memória nos testes.

O frontend espelha isso com um layout **modular / fatiado por feature**: cada
feature (`exam-upload`, `dashboard`, `analysis-history`, `analysis-detail`,
`auth`) possui seus próprios `components/`, `hooks/`, `services/`, `types/`,
`pages/`, com blocos reutilizáveis em `shared/`.

Detalhamento completo: **[docs/architecture.md](docs/architecture.md)**.

## Pipeline de IA

```
bytes → validação (Pillow) → pré-processamento (resize + normalização)
      → motor de inferência (torchxrayvision | pesos próprios | mock)
      → score → portão de incerteza → value object Prediction → persistido
```

- **Modelo real (padrão no Docker):** uma **DenseNet do torchxrayvision**
  (`densenet121-res224-all`), pré-treinada em grandes datasets públicos de
  raio-X de tórax. Ela gera probabilidades por patologia; usamos `Pneumonia` /
  `Consolidation` / `Lung Opacity` para classificar `NORMAL` / `PNEUMONIA` /
  `UNCERTAIN`.
- **Pesos próprios:** defina `MODEL_WEIGHTS_PATH` para um checkpoint ajustado seu.
- **Motor mock (fallback):** determinístico, sem torch — mantém o projeto
  executável sem a stack pesada de ML (CI, clones rápidos). Force com
  `USE_MOCK_INFERENCE=true`. Não é um classificador; só exercita o pipeline.
  Os três retornam o **mesmo contrato `Prediction`**.
- **Portão de incerteza:** scores ambíguos viram `UNCERTAIN` em vez de forçar
  uma resposta confiante e errada.

Detalhes: **[docs/ai-model.md](docs/ai-model.md)**.

## Fluxo de dados

```
Navegador ──upload──▶ FastAPI ──salva img──▶ Storage (local / S3)
                         │
                         ├── insere Analysis(PENDING) ──▶ PostgreSQL
                         └── enfileira tarefa ──▶ RabbitMQ ──▶ worker Celery
                                                                  │
                                    pré-processa + inferência ◀───┘
                                              │
                                    atualiza Analysis(COMPLETED) ──▶ PostgreSQL
Navegador ◀──poll GET /analysis/{id}── FastAPI
```

## Endpoints da API

| Método | Caminho                      | Descrição                          |
|--------|------------------------------|------------------------------------|
| GET    | `/health`                    | Verificação de saúde               |
| POST   | `/api/v1/analysis/upload`    | Envia imagem e cria análise        |
| GET    | `/api/v1/analysis`           | Lista análises (filtros status/classe) |
| GET    | `/api/v1/analysis/{id}`      | Obtém uma análise                  |
| DELETE | `/api/v1/analysis/{id}`      | Remove uma análise e sua imagem    |
| GET    | `/api/v1/dashboard/summary`  | Métricas agregadas do dashboard    |

Documentação interativa (Swagger UI) em `http://localhost:8000/docs`.

## Como executar localmente

### Opção A — Docker Compose (recomendado)

```bash
cp .env.example .env
make up          # builda e sobe api, worker, postgres, rabbitmq, frontend
make seed        # (opcional) popula análises sintéticas para o dashboard
```

- Frontend: <http://localhost:5173>
- Docs da API: <http://localhost:8000/docs>
- UI do RabbitMQ: <http://localhost:15672> (guest/guest)

```bash
make down        # para tudo
```

### Opção B — serviços manualmente

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
# em outro terminal: celery -A worker.celery_app worker --loglevel=info

# Frontend
cd frontend
npm install
npm run dev
```

## Testes

```bash
make backend-test     # pytest (casos de uso, repositório, inferência, API)
make frontend-test    # vitest (componentes + validação)
make e2e              # Playwright (início → upload → enviar → detalhe)
make test             # testes unitários de backend + frontend
```

A suíte de backend roda **sem serviços externos** — persistência, storage e fila
são substituídos por fakes em memória através das portas do domínio.

## CI/CD

O GitHub Actions (`.github/workflows/ci.yml`) roda em cada push/PR:

1. **Backend** — instala dependências, lint `ruff`, `pytest`.
2. **Frontend** — instala dependências, `eslint`, `vitest`, type-check + `vite build`.
3. **Docker** — builda as duas imagens para detectar regressões de container.

## Arquitetura cloud-ready (AWS)

O design de portas/adaptadores torna a migração para a nuvem uma questão de
trocar adaptadores, não de reescrever a lógica:

| Local                         | AWS                                            |
|-------------------------------|------------------------------------------------|
| Armazenamento local           | **S3** (troca `LocalFileStorage` → `S3Storage`) |
| Container PostgreSQL          | **Aurora PostgreSQL (Serverless v2)**          |
| Container RabbitMQ            | **Amazon MQ** (RabbitMQ) ou **SQS**            |
| Container do worker Celery    | Serviço **ECS/Fargate** ou **Lambda**          |
| Container FastAPI             | **ECS/Fargate** atrás de um **ALB**            |
| Imagens Docker locais         | **ECR**                                        |
| Logs em stdout                | **CloudWatch Logs**                            |
| Vite dev server / nginx       | **S3 + CloudFront** (hosting estático + CDN)   |

Design completo + diagrama: **[docs/cloud-aws.md](docs/cloud-aws.md)**.

## Melhorias futuras

- Treinar e publicar um modelo real de raio-X (ex.: transfer learning em dataset
  público de pneumonia) e adicionar mapas de calor Grad-CAM para explicabilidade.
- Autenticação e histórico por usuário (a entidade `User` e a feature `auth` já
  estão esboçadas).
- Adaptador de object storage (S3) + URLs de upload pré-assinadas.
- Observabilidade: logs estruturados em JSON, métricas, tracing.
- Versionamento de modelo e métricas de avaliação (precisão/recall, scikit-learn)
  exibidas no dashboard.

## Licença

Distribuído sob a [Licença MIT](LICENSE).

## Aviso legal

**Este projeto é apenas para fins educacionais e de portfólio. Não é uma
ferramenta de diagnóstico médico.** A saída da IA é uma demonstração de um
pipeline de engenharia e nunca deve embasar decisões médicas reais.
