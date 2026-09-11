# DevOps Shack AI Forward Deployed Engineering (AI FDE) Platform

> Enterprise polyglot microservices modernized with **RAG (Chroma DB)**, **Production Guardrails**, and an **Automated Evaluations (Evals)** suite.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![Chroma DB](https://img.shields.io/badge/Chroma_DB-Vector_Store-red.svg?style=flat)](https://trychroma.com)
[![Docker](https://img.shields.io/badge/Docker-11_Containers-2496ED.svg?style=flat&logo=docker)](https://docker.com)
[![Pytest](https://img.shields.io/badge/Tests-21_Passed_100%25-brightgreen.svg?style=flat)]()
[![Evals Health](https://img.shields.io/badge/Evals_Health-EXCELLENT_(93.8%25)-blue.svg?style=flat)]()
[![Guardrails](https://img.shields.io/badge/Guardrails-100%25_Defense-success.svg?style=flat)]()

---

## 📌 Overview & AI FDE Role

This project demonstrates an **AI Forward Deployed Engineer (AI FDE)** end-to-end workflow: studying an enterprise polyglot microservices mesh across **7 programming languages**, identifying operational friction, and integrating a production-grade **Python FastAPI AI Assistant** equipped with:
- **Retrieval-Augmented Generation (RAG)** grounded in **Chroma DB Vector Store** (17 internal specs & policy documents).
- **Enterprise Guardrails Subsystem** (Prompt injection/DAN defense, PII masking, domain scope enforcement, output secret leak prevention).
- **Automated Evaluations (Evals) Suite** (16 golden benchmarks measuring Faithfulness, Relevance, Pricing Accuracy, and Defense).
- **Full-Stack UI** (Omnipresent floating AI Widget + interactive 3-tab AI Control Center in React).

---

## 🏛️ Architecture & Services

```text
React Web UI (:5173) + AI Widget
       │
       ▼
AI Assistant (:8088) ───► Chroma DB (:8000) [17 Knowledge Documents]
       │
       ├─► Go Catalog Service (:8082)
       ├─► Node.js Inventory Service (:8083)
       └─► PostgreSQL (:5432) [7 Isolated Schemas]
```

### Microservices Mesh Topology

| Port | Service | Tech Stack | Responsibility |
|---|---|---|---|
| **5173** | **Commerce Web UI** | React 18 + Vite | Storefront, Floating AI Widget, AI Control Center |
| **8088** | **AI Assistant** | Python FastAPI | RAG, Pricing Engine, Guardrails & Evals Suite |
| **8000** | **Chroma DB** | Vector Database | Semantic embeddings for internal knowledge |
| **8081** | **Auth Service** | Java 21 (Spring Boot) | JWT authentication & user sessions |
| **8082** | **Catalog Service** | Go 1.22 | Product inventory & search |
| **8083** | **Inventory Service** | Node.js (Express) | Real-time stock reservation |
| **8084** | **Order Service** | Python FastAPI | Checkout orchestrator & order lifecycle |
| **8085** | **Payment Service** | C# (ASP.NET Core 8) | Payment authorization & refunds |
| **8086** | **Notification Service** | Ruby (Sinatra) | Email & SMS notification alerts |
| **8087** | **Analytics Service** | PHP 8.2 | Cross-service KPI aggregator |
| **5432** | **PostgreSQL** | PostgreSQL 16 Alpine | 7 isolated microservice databases |

---

## 📁 Project Folder Structure

```text
devops-shack-ai-fde-platform/
├── docker-compose.yml                  # 11-service orchestration
├── database/bootstrap.sql              # Auto-provisions 7 PostgreSQL schemas
├── frontend/                           # React 18 + Vite SPA (:5173)
│   └── src/
│       ├── AIWidget.jsx                # Floating AI chat drawer component
│       ├── AssistantView.jsx           # AI Control Center (RAG, Guardrails, Evals)
│       └── App.jsx                     # Main application shell
└── services/
    ├── ai-assistant-service/           # 🤖 AI Assistant (:8088)
    │   ├── app/
    │   │   ├── assistant.py            # Conversational orchestrator & fallback
    │   │   ├── guardrails/             # 🛡️ Injections, PII, Scope, Secret leak filters
    │   │   ├── rag/                    # 📚 Chroma DB retriever & 17 knowledge docs
    │   │   ├── evals/                  # 📊 16 Golden benchmark test cases & metrics
    │   │   └── pricing_engine.py       # Tiered volume discounts & promo codes
    │   ├── tests/                      # 21 automated pytest unit & eval tests
    │   └── scripts/verify_endpoints.py # REST verification script
    ├── auth-service/                   # Java 21 Spring Boot (:8081)
    ├── catalog-service/                # Go 1.22 (:8082)
    ├── inventory-service/              # Node.js 20 Express (:8083)
    ├── order-service/                  # Python FastAPI (:8084)
    ├── payment-service/                # C# ASP.NET Core 8 (:8085)
    ├── notification-service/           # Ruby 3.3 Sinatra (:8086)
    └── analytics-service/              # PHP 8.2 (:8087)
```

---

## 🛡️ Enterprise Guardrails & Evals Summary

### 1. Guardrail Protection Layers
- **Prompt Injection Defense**: Intercepts instruction overrides, `DAN` jailbreaks, and system prompt extraction attacks.
- **PII & Secret Redaction**: Automatically masks credit cards (Visa/Mastercard/Amex), SSNs, JWTs, and OpenAI API keys.
- **Domain Scope Classifier**: Enforces boundaries strictly to ecommerce hardware, specs, quotes, and architecture.
- **Output Leak Prevention**: Sanitizes responses post-flight to prevent database credentials from leaking.

### 2. Benchmark Scorecard (16 Golden Cases)
- **Overall Health**: `EXCELLENT` (93.8% pass rate, 15/16 passed)
- **RAG Faithfulness**: `95.0%`
- **Pricing Accuracy**: `88.8%`
- **Guardrail Defense Rate**: `100.0%`
- **Test Suite**: 21/21 pytest unit tests passed (`tests/test_*.py`)

---

## 🚀 Quick Start (Docker Compose)

### 1. Configure Environment
```bash
cp .env.openai.example .env.openai
```
*(Optional: Add `OPENAI_API_KEY`. If omitted, local deterministic RAG engine runs automatically with zero downtime.)*

### 2. Launch All 11 Services
```bash
docker compose up --build -d
```

### 3. Access Applications
- **Web UI & Floating AI Widget**: [http://localhost:5173](http://localhost:5173)
- **AI Assistant Control Center**: [http://localhost:5173/assistant](http://localhost:5173/assistant)
- **AI Assistant Swagger Docs**: [http://localhost:8088/docs](http://localhost:8088/docs)
- **Chroma DB Heartbeat**: [http://localhost:8000/api/v1/heartbeat](http://localhost:8000/api/v1/heartbeat)

### 4. Stop Services
```bash
docker compose down      # Preserves database data
docker compose down -v   # Clean volume reset
```

---

## 💻 Local Development (Without Docker)

#### AI Assistant Service:
```bash
cd services/ai-assistant-service
pip install -r requirements.txt

# Run all 21 automated tests (100% pass)
python -m pytest tests/ -v

# Run verification script
python scripts/verify_endpoints.py

# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
```

#### React Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 Key REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health & Chroma DB status |
| `POST` | `/assistant/chat` | Chat with Guardrail pre-flight & RAG context |
| `POST` | `/assistant/guardrails/check` | Real-time text scanner for injections and PII |
| `GET` | `/assistant/guardrails/policies` | Active guardrail rules and severity levels |
| `POST` | `/assistant/evals/run` | Execute automated 16-case benchmark evaluation suite |
| `GET` | `/assistant/evals/results` | Retrieve cached evaluation scorecard and test matrix |
| `POST` | `/assistant/rag/query` | Direct semantic search into Chroma DB vector store |
| `POST` | `/assistant/pricing/calculate` | Direct programmatic pricing quote calculator |

---

## 📄 License & Author

Created by **Bittu Sharma** for the **DevOps Shack AI Forward Deployed Engineer (AI FDE)** platform showcase.
