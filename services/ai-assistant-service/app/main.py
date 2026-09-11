import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from contextlib import asynccontextmanager
from app.config import settings
from app.assistant import assistant
from app.catalog_client import catalog_client
from app.pricing_engine import pricing_engine
from app.rag.chroma_client import chroma_manager
from app.rag.indexer import knowledge_indexer
from app.rag.retriever import rag_retriever
from app.guardrails.manager import guardrail_manager
from app.evals.runner import eval_runner
from app.evals.dataset import GOLDEN_EVAL_DATASET

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure Chroma DB knowledge base is indexed on startup
    await knowledge_indexer.ensure_indexed()
    yield

app = FastAPI(
    title="DevOps Shack AI Assistant Service",
    version="1.0.0",
    description="Python FastAPI AI Assistant with RAG via Chroma DB and OpenAI API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------
# Request Models
# -----------------

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query or instruction")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation messages")

class ItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)

class PricingRequest(BaseModel):
    items: List[ItemRequest] = Field(..., min_length=1)
    promo_code: Optional[str] = Field(default=None, description="Promo code e.g. DEVOPS10")
    tax_rate: Optional[float] = Field(default=0.08, ge=0.0, le=1.0)

class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query for internal knowledge")
    n_results: Optional[int] = Field(default=3, ge=1, le=10)
    category: Optional[str] = Field(default=None)

class GuardrailCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to scan against guardrail policies")

class EvalRunRequest(BaseModel):
    limit: Optional[int] = Field(default=None, ge=1, le=50, description="Optional limit on test cases to run")

# -----------------
# Endpoints
# -----------------

@app.get("/health")
def health():
    """Health check endpoint following the project's standard microservice format."""
    return {
        "service": "ai-assistant-service",
        "status": "UP",
        "language": "Python",
        "openai_configured": settings.is_openai_configured(),
        "model": settings.OPENAI_MODEL,
        "env_source": settings.ENV_SOURCE,
        "rag": chroma_manager.status,
        "guardrails_active": True,
        "evals_available": True,
    }

@app.get("/assistant/rag/status")
def get_rag_status():
    """Inspect Chroma DB connection status, collection, and document count."""
    return chroma_manager.status

@app.post("/assistant/rag/reindex")
async def trigger_rag_reindex():
    """Trigger manual reindexing of app knowledge and live catalog into Chroma DB."""
    return await knowledge_indexer.index_knowledge_base(force=True)

@app.post("/assistant/rag/query")
def query_rag_knowledge(payload: RAGQueryRequest):
    """Direct semantic similarity search into Chroma DB vector store."""
    return rag_retriever.query(
        query_text=payload.query,
        n_results=payload.n_results or 3,
        category=payload.category,
    )

@app.get("/assistant/config")
def get_config_status():
    """Inspect assistant configuration and OpenAI status."""
    return {
        "service": "ai-assistant-service",
        "openai_configured": settings.is_openai_configured(),
        "model": settings.OPENAI_MODEL,
        "catalog_url": settings.CATALOG_URL,
        "inventory_url": settings.INVENTORY_URL,
        "env_file_loaded": settings.ENV_SOURCE,
    }

@app.get("/assistant/products")
async def list_products():
    """Retrieve all products known to the assistant."""
    return await catalog_client.get_all_products()

@app.post("/assistant/pricing/calculate")
async def calculate_pricing_endpoint(payload: PricingRequest):
    """Direct pricing calculation endpoint for carts or item lists."""
    enriched_items = []
    for it in payload.items:
        prod = await catalog_client.get_product_by_id(it.product_id)
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product with ID {it.product_id} not found")
        enriched_items.append({
            "product_id": prod["id"],
            "name": prod["name"],
            "price": prod["price"],
            "quantity": it.quantity,
        })

    return pricing_engine.calculate(
        items=enriched_items,
        promo_code=payload.promo_code,
        tax_rate=payload.tax_rate or 0.08,
    )

@app.post("/assistant/chat")
async def chat_endpoint(payload: ChatRequest):
    """
    Main conversational endpoint.
    Accepts user message and history, returns assistant reply.
    """
    history_dicts = [{"role": m.role, "content": m.content} for m in payload.history] if payload.history else []
    result = await assistant.chat(
        message=payload.message,
        history=history_dicts,
    )
    return result

@app.post("/assistant/guardrails/check")
def check_guardrails_endpoint(payload: GuardrailCheckRequest):
    """Scan arbitrary input text for prompt injection, PII, and out-of-scope topics."""
    res = guardrail_manager.check_input(payload.text)
    return res.model_dump()

@app.get("/assistant/guardrails/policies")
def get_guardrails_policies():
    """Retrieve active guardrail policies and security rules."""
    return guardrail_manager.policies

@app.post("/assistant/evals/run")
async def run_evals_suite(payload: Optional[EvalRunRequest] = None):
    """Execute automated evaluation benchmark suite across RAG, pricing, and guardrails."""
    limit = payload.limit if payload else None
    return await eval_runner.run_suite(limit=limit)

@app.get("/assistant/evals/results")
def get_evals_results():
    """Retrieve the latest completed evaluation benchmark results."""
    return eval_runner.latest_results or {
        "status": "not_run_yet",
        "message": "No evaluations have been run in this session. Trigger POST /assistant/evals/run to start.",
    }

@app.get("/assistant/evals/dataset")
def get_evals_dataset():
    """Retrieve the golden benchmark dataset test cases."""
    return {
        "total_cases": len(GOLDEN_EVAL_DATASET),
        "cases": GOLDEN_EVAL_DATASET,
    }

@app.get("/")
def root():
    """Service status and API information."""
    return {
        "service": "ai-assistant-service",
        "status": "UP",
        "language": "Python",
        "docs_url": "/docs",
        "health_url": "/health",
        "rag_status_url": "/assistant/rag/status",
        "guardrails_url": "/assistant/guardrails/policies",
        "evals_url": "/assistant/evals/results",
        "endpoints": [
            "POST /assistant/chat",
            "POST /assistant/pricing/calculate",
            "GET /assistant/products",
            "GET /assistant/rag/status",
            "POST /assistant/rag/query",
            "POST /assistant/rag/reindex",
            "POST /assistant/guardrails/check",
            "GET /assistant/guardrails/policies",
            "POST /assistant/evals/run",
            "GET /assistant/evals/results",
            "GET /assistant/evals/dataset",
            "GET /health",
        ],
    }
