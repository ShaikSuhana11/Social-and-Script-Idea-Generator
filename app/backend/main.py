import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routes.content import router as content_router
from app.backend.schemas import HealthResponse
from app.services.rag_service import initialize_knowledge_base, get_rag_service
from app.services.llm_service import get_llm_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    try:
        chunks = initialize_knowledge_base()
        logger.info("RAG initialized: %s chunks", chunks)
    except Exception as e:
        logger.exception("RAG init failed: %s", e)
    try:
        get_llm_service()
        logger.info("LLM ready")
    except Exception as e:
        logger.exception("LLM init failed: %s", e)
    yield
    logger.info("Shutting down...")

app = FastAPI(title="AI Social Media Generator", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(content_router)

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", llm_ready=True, rag_chunks=get_rag_service().collection.count())