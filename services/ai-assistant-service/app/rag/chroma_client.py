import logging
import os
from typing import Optional, Tuple
import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

logger = logging.getLogger(__name__)

class ChromaClientManager:
    def __init__(self):
        self._client: Optional[chromadb.ClientAPI] = None
        self._is_http_remote: bool = False
        self._collection = None
        self._embedding_function = None
        self._embedding_model_name: str = "all-MiniLM-L6-v2"

    def _get_embedding_function(self):
        # Use local DefaultEmbeddingFunction to ensure full offline capability and zero quota dependencies
        self._embedding_model_name = "chroma/all-MiniLM-L6-v2"
        return embedding_functions.DefaultEmbeddingFunction()

    def get_client(self) -> Tuple[chromadb.ClientAPI, bool]:
        """
        Connect to Chroma DB container via HTTP client.
        Falls back to local persistent client if container is unreachable.
        """
        if self._client is not None:
            return self._client, self._is_http_remote

        # 1. Attempt connection to Chroma DB container
        try:
            http_client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            # Test heartbeat
            http_client.heartbeat()
            self._client = http_client
            self._is_http_remote = True
            logger.info(f"Connected to Chroma DB Docker container at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
            return self._client, True
        except Exception as e:
            logger.info(
                f"Chroma DB container at {settings.CHROMA_HOST}:{settings.CHROMA_PORT} not reachable ({e}). "
                f"Using local persistent Chroma DB in '{settings.CHROMA_DATA_DIR}'."
            )

        # 2. Fallback to local persistent storage
        try:
            os.makedirs(settings.CHROMA_DATA_DIR, exist_ok=True)
            self._client = chromadb.PersistentClient(path=settings.CHROMA_DATA_DIR)
            self._is_http_remote = False
            return self._client, False
        except Exception as err:
            logger.error(f"Failed to create persistent Chroma client: {err}")
            # In-memory ephemeral fallback as ultimate safety net
            self._client = chromadb.EphemeralClient()
            self._is_http_remote = False
            return self._client, False

    def get_collection(self):
        """Get or create the knowledge collection with the configured embedding function."""
        if self._collection is not None:
            return self._collection

        client, _ = self.get_client()
        self._embedding_function = self._get_embedding_function()

        try:
            self._collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                embedding_function=self._embedding_function,
                metadata={"description": "Polyglot Commerce Internal App Knowledge Base"},
            )
        except Exception as e:
            if "Embedding function conflict" in str(e):
                logger.warning(f"Chroma DB embedding function conflict ({e}); getting existing collection.")
                try:
                    self._collection = client.get_collection(name=settings.CHROMA_COLLECTION)
                except Exception:
                    client.delete_collection(name=settings.CHROMA_COLLECTION)
                    self._collection = client.create_collection(
                        name=settings.CHROMA_COLLECTION,
                        embedding_function=self._embedding_function,
                        metadata={"description": "Polyglot Commerce Internal App Knowledge Base"},
                    )
            else:
                raise e
        return self._collection

    @property
    def status(self) -> dict:
        client, is_remote = self.get_client()
        coll = self.get_collection()
        doc_count = coll.count() if coll else 0
        return {
            "chroma_mode": "docker_container" if is_remote else "local_persistent",
            "host": settings.CHROMA_HOST if is_remote else "localhost (embedded)",
            "port": settings.CHROMA_PORT if is_remote else None,
            "collection": settings.CHROMA_COLLECTION,
            "embedding_model": self._embedding_model_name,
            "documents_indexed": doc_count,
        }

chroma_manager = ChromaClientManager()
