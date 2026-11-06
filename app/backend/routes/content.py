import logging
from fastapi import APIRouter, HTTPException
from app.backend.schemas import ContentRequest, ContentResponse
from app.services.llm_service import get_llm_service, LLMServiceError
from app.services.rag_service import get_rag_service
from app.services.prompt_service import SYSTEM_PROMPT, build_content_prompt

logger = logging.getLogger(__name__)

# The route is defined here with the /api prefix
router = APIRouter(prefix="/api", tags=["content"])

@router.post("/generate", response_model=ContentResponse)
async def generate_content(req: ContentRequest):
    try:
        rag_service = get_rag_service()
        context = ""
        rag_used = False

        # If use_rag is true, get context from the knowledge base
        if req.use_rag:
            context = rag_service.retrieve(query=f"{req.platform} {req.topic}", top_k=2)
            rag_used = bool(context)

        # Build the prompt using the inputs from the schema
        prompt = build_content_prompt(
            topic=req.topic,
            platform=req.platform,
            tone=req.tone,
            audience=req.audience,
            content_type=req.content_type,
            num_recommendations=req.num_recommendations, 
            context=context
        )

        # Generate the content using the LLM
        llm = get_llm_service()
        content = llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=2048
        )

        # Return the response matching the ContentResponse schema
        return ContentResponse(
            content=content,
            platform=req.platform,
            topic=req.topic,
            rag_used=rag_used,
            model=llm.model
        )

    except LLMServiceError as e:
        # Catch specific LLM errors (e.g., API key invalid)
        raise HTTPException(status_code=502, detail=f"LLM service error: {str(e)}")
    except Exception as e:
        # Catch any other unexpected errors
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
