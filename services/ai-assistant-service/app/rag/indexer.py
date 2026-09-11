import logging
from typing import Dict, Any, List
from app.rag.chroma_client import chroma_manager
from app.rag.knowledge_base import INTERNAL_KNOWLEDGE
from app.catalog_client import catalog_client

logger = logging.getLogger(__name__)

class KnowledgeIndexer:
    @staticmethod
    async def index_knowledge_base(force: bool = False) -> Dict[str, Any]:
        """
        Embeds and upserts internal documents and dynamic catalog products into Chroma DB.
        """
        collection = chroma_manager.get_collection()
        current_count = collection.count()

        if current_count > 0 and not force:
            logger.info(f"Knowledge base already indexed with {current_count} documents.")
            return {
                "status": "already_indexed",
                "count": current_count,
                "collection": collection.name,
            }

        documents: List[str] = []
        ids: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        # 1. Ingest curated internal knowledge
        for item in INTERNAL_KNOWLEDGE:
            doc_id = item["id"]
            content = f"[{item['title']}] ({item['category']}): {item['content']}"
            documents.append(content)
            ids.append(doc_id)
            metadatas.append({
                "title": item["title"],
                "category": item["category"],
                "tags": ",".join(item.get("tags", [])),
                "source": "internal_knowledge_base",
            })

        # 2. Dynamically ingest live products from catalog service
        try:
            live_products = await catalog_client.get_all_products()
            for p in live_products:
                doc_id = f"live-product-{p['id']}"
                # If product already covered by curated specs, update or add live data
                p_desc = (
                    f"Product Name: {p['name']} (ID: {p['id']}). "
                    f"Category: {p['category']}. "
                    f"Price: ${p['price']:.2f}. "
                    f"Icon: {p.get('image', '📦')}. "
                    f"Active: {p.get('active', True)}. "
                    f"Description: {p.get('description', '')}. "
                    f"Current Stock: {p.get('stock', 'Available')} units."
                )
                documents.append(p_desc)
                ids.append(doc_id)
                metadatas.append({
                    "title": p["name"],
                    "category": p["category"],
                    "tags": f"live_catalog,product,{p['category'].lower()}",
                    "source": "live_catalog_api",
                })
        except Exception as e:
            logger.warning(f"Could not fetch live catalog items for RAG indexing ({e})")

        # Upsert documents into Chroma DB
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )

        total_count = collection.count()
        logger.info(f"Successfully indexed {len(documents)} documents into Chroma DB '{collection.name}'")

        return {
            "status": "indexed",
            "indexed_count": len(documents),
            "total_documents": total_count,
            "collection": collection.name,
        }

    @classmethod
    async def ensure_indexed(cls):
        """Auto-index on service startup if collection is empty."""
        try:
            coll = chroma_manager.get_collection()
            if coll.count() == 0:
                logger.info("Chroma DB collection empty. Starting initial knowledge base indexing...")
                await cls.index_knowledge_base(force=True)
        except Exception as e:
            logger.error(f"Error checking/indexing knowledge base: {e}")

knowledge_indexer = KnowledgeIndexer()
