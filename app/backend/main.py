import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routes.content import router as content_router
from app.backend.schemas import HealthResponse
from app.services.rag_service import get_rag_service
from app.services.llm_service import get_llm_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    
    # 1. Initialize LLM (This is safe, doesn't use much memory)
    try:
        get_llm_service()
        logger.info("LLM ready")
    except Exception as e:
        logger.exception("LLM init failed: %s", e)
        
    # 2. REMOVED initialize_knowledge_base() from here!
    # We are letting the RAG service lazy-load on the first user request to save memory.
    logger.info("RAG will be initialized lazily on the first request.")
    
    yield
    logger.info("Shutting down...")

app = FastAPI(title="AI Social Media Generator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.include_router(content_router)

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health", response_model=HealthResponse)
async def health():
    # Safely get the count without triggering a full load if possible
    try:
        rag = get_rag_service()
        # If the collection hasn't been loaded yet, this will be 0
        chunks = rag._collection.count() if rag._collection else 0
    except Exception:
        chunks = 0
        
    return HealthResponse(status="healthy", llm_ready=True, rag_chunks=chunks)
