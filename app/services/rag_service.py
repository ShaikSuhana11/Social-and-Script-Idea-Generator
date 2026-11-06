
"""ChromaDB setup, ingestion, and retrieval for RAG with Lazy Loading."""

import os

# --- CRITICAL MEMORY LIMITS FOR RENDER FREE TIER ---
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
KNOWLEDGE_FILE = Path(__file__).resolve().parent.parent / "data" / "knowledge.txt"
COLLECTION_NAME = "brand_knowledge"


class RAGService:
    """ChromaDB-backed retrieval service with Lazy Loading."""

    def __init__(self, db_path: str = CHROMA_DB_PATH):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)

        # Initialize ChromaDB (this uses very little memory)
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # DO NOT load the embedding model or collection here. Keep them as None.
        self._embed_fn = None
        self._collection = None

    def _get_embed_fn(self):
        """Lazy load the embedding model only when needed."""
        if self._embed_fn is None:
            import torch
            torch.set_num_threads(1) # Save memory
            print("[RAG] Loading embedding model into memory...")
            self._embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        return self._embed_fn

    def _get_collection(self):
        """Lazy load the collection only when needed."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self._get_embed_fn(),
            )
        return self._collection

    def ingest_file(self, file_path: Path = KNOWLEDGE_FILE) -> int:
        """Load and index a text file into ChromaDB. Returns number of chunks."""
        if not file_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {file_path}")

        collection = self._get_collection() # Trigger lazy load

        # If already ingested, skip to save memory and time
        if collection.count() > 0:
            return collection.count()

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = self._chunk_text(content)
        if not chunks:
            return 0

        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": str(file_path), "chunk_index": i} for i in range(len(chunks))]

        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        return len(chunks)

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks by characters."""
        text = text.strip()
        if not text:
            return []

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end].strip())
            start = end - overlap if end < len(text) else len(text)

        return [c for c in chunks if c]

    def retrieve(self, query: str, top_k: int = 1) -> str:
        """Return concatenated relevant context for a query."""
        collection = self._get_collection() # Trigger lazy load
        
        # Auto-ingest if database is empty
        if collection.count() == 0:
            self.ingest_file()

        try:
            results = collection.query(query_texts=[query], n_results=top_k)
            docs = results.get("documents", [[]])[0]
            return "\n\n---\n\n".join(docs)
        except Exception as e:
            print(f"[RAG] Retrieval error: {e}")
            return ""


_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

def initialize_knowledge_base() -> int:
    """Ingest knowledge file on startup."""
    service = get_rag_service()
    return service.ingest_file()

