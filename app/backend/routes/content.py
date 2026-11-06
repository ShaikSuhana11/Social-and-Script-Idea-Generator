import logging
from fastapi import APIRouter, HTTPException
from app.backend.schemas import ContentRequest, ContentResponse
from app.services.llm_service import get_llm_service, LLMServiceError
from app.services.rag_service import get_rag_service
from app.services.prompt_service import SYSTEM_PROMPT, build_content_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["content"])

@router.post("/generate", response_model=ContentResponse)
async def generate_content(req: ContentRequest):
    try:
        rag_service = get_rag_service()
        context = ""
        rag_used = False

        if req.use_rag:
            context = rag_service.retrieve(query=f"{req.platform} {req.topic}", top_k=2)
            rag_used = bool(context)

        # Pass num_recommendations to the prompt builder
        prompt = build_content_prompt(
            topic=req.topic,
            platform=req.platform,
            tone=req.tone,
            audience=req.audience,
            content_type=req.content_type,
            num_recommendations=req.num_recommendations, 
            context=context
        )

        llm = get_llm_service()
        content = llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=2048
        )

        return ContentResponse(
            content=content,
            platform=req.platform,
            topic=req.topic,
            rag_used=rag_used,
            model=llm.model
        )

    except LLMServiceError as e:
        raise HTTPException(status_code=502, detail=f"LLM service error: {str(e)}")
    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")