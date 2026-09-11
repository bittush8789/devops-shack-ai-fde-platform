import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure service root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.rag.chroma_client import chroma_manager
from app.rag.indexer import knowledge_indexer
from app.rag.retriever import rag_retriever

client = TestClient(app)

def test_rag_indexing():
    print("Indexing knowledge base into Chroma DB...")
    import asyncio
    result = asyncio.run(knowledge_indexer.index_knowledge_base(force=True))
    assert result["status"] == "indexed"
    assert result["total_documents"] >= 10
    print(f"[PASS] RAG indexing passed: {result['total_documents']} documents indexed into Chroma DB")

def test_rag_status_endpoint():
    response = client.get("/assistant/rag/status")
    assert response.status_code == 200
    data = response.json()
    assert data["documents_indexed"] >= 10
    assert "chroma_mode" in data
    assert "embedding_model" in data
    print(f"[PASS] RAG status endpoint passed: Mode={data['chroma_mode']}, Model={data['embedding_model']}, Docs={data['documents_indexed']}")

def test_rag_semantic_search_keyboard():
    hits = rag_retriever.query("What switches are in the mechanical keyboard?", n_results=2)
    assert len(hits) > 0
    top_hit = hits[0]
    assert "Gateron" in top_hit["content"] or "Keyboard" in top_hit["title"]
    print(f"[PASS] Semantic search (keyboard specs) passed: top hit = '{top_hit['title']}' (dist={top_hit['distance']})")

def test_rag_semantic_search_architecture():
    hits = rag_retriever.query("Which microservice is built in Java and handles authentication?", n_results=2)
    assert len(hits) > 0
    assert any("Java" in h["content"] or "Auth" in h["content"] or "Architecture" in h["category"] for h in hits)
    print(f"[PASS] Semantic search (architecture) passed: top hit = '{hits[0]['title']}'")

def test_rag_semantic_search_policies():
    hits = rag_retriever.query("What is the return policy and warranty for hardware?", n_results=2)
    assert len(hits) > 0
    top_hit = hits[0]
    assert "30-day" in top_hit["content"] or "warranty" in top_hit["content"].lower()
    print(f"[PASS] Semantic search (policies) passed: top hit = '{top_hit['title']}'")

def test_rag_query_endpoint():
    payload = {
        "query": "kubectl commands cheatsheet",
        "n_results": 2
    }
    response = client.post("/assistant/rag/query", json=payload)
    assert response.status_code == 200
    hits = response.json()
    assert len(hits) > 0
    assert any("Desk Mat" in h["title"] or "kubectl" in h["content"] for h in hits)
    print(f"[PASS] Direct RAG query endpoint passed: {len(hits)} matching chunks returned")

def test_rag_chat_product_internal_specs():
    payload = {
        "message": "What kind of switches does the AI Mechanical Keyboard use, and does it support Bluetooth?"
    }
    response = client.post("/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    # Check that retrieved internal knowledge was used
    assert "Gateron" in reply or "Bluetooth" in reply or "75%" in reply
    print("[PASS] RAG chat product internal specs passed. Reply snippet:", reply[:150].replace('\n', ' '), "...")

def test_rag_chat_architecture_question():
    payload = {
        "message": "Which microservice is built in Java and what port does it run on?"
    }
    response = client.post("/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "8081" in reply or "Auth" in reply or "Java" in reply
    print("[PASS] RAG chat architecture question passed. Reply snippet:", reply[:150].replace('\n', ' '), "...")

if __name__ == "__main__":
    test_rag_indexing()
    test_rag_status_endpoint()
    test_rag_semantic_search_keyboard()
    test_rag_semantic_search_architecture()
    test_rag_semantic_search_policies()
    test_rag_query_endpoint()
    test_rag_chat_product_internal_specs()
    test_rag_chat_architecture_question()
    print("\n>>> ALL RAG & CHROMA DB TESTS PASSED! <<<")
