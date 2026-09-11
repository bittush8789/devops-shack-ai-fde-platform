import logging
from typing import List, Dict, Any, Optional
from app.rag.chroma_client import chroma_manager

logger = logging.getLogger(__name__)

class RAGRetriever:
    @staticmethod
    def query(
        query_text: str,
        n_results: int = 3,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query Chroma DB for semantically similar documents.
        """
        try:
            collection = chroma_manager.get_collection()
            count = collection.count()
            if count == 0:
                return []

            k = min(n_results, count)
            where_filter = {"category": category} if category else None

            results = collection.query(
                query_texts=[query_text],
                n_results=k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )

            hits = []
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i in range(len(docs)):
                meta = metas[i] if i < len(metas) else {}
                dist = distances[i] if i < len(distances) else 0.0
                hits.append({
                    "content": docs[i],
                    "title": meta.get("title", "Internal Document"),
                    "category": meta.get("category", "General"),
                    "source": meta.get("source", "internal_kb"),
                    "distance": round(float(dist), 4),
                })

            return hits
        except Exception as e:
            logger.error(f"Error querying Chroma DB: {e}")
            return []

    @classmethod
    def get_formatted_context(cls, query_text: str, n_results: int = 3) -> str:
        """
        Retrieve relevant knowledge chunks formatted for injection into the assistant's context.
        """
        hits = cls.query(query_text, n_results=n_results)
        if not hits:
            return ""

        context_blocks = ["### 📚 Retrieved Internal App & Product Knowledge:"]
        for idx, hit in enumerate(hits, start=1):
            context_blocks.append(
                f"[{idx}] {hit['title']} (Category: {hit['category']}):\n{hit['content']}"
            )

        return "\n\n".join(context_blocks)

rag_retriever = RAGRetriever()
