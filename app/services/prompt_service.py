from typing import Optional

SYSTEM_PROMPT = """You are an expert social media content strategist and copywriter.
You write platform-optimized, on-brand content that drives engagement.
Always follow the brand knowledge base provided. Be concise, compelling, and original.
Return ONLY the final content — no preamble, no explanations."""

def build_content_prompt(topic: str, platform: str, tone: str, audience: str, content_type: str, num_recommendations: int, context: Optional[str] = None) -> str:
    
    context_block = f"\n\nBRAND KNOWLEDGE CONTEXT:\n{context}" if context else ""
    
    # Use the dynamic number of recommendations here
    if content_type == "ideas":
        task = f"Generate exactly {num_recommendations} creative content ideas. Provide a catchy title, short description, and format for each."
    elif content_type == "captions":
        task = f"Write exactly {num_recommendations} engaging captions with relevant hashtags and a strong CTA."
    elif content_type == "script":
        task = f"Write exactly {num_recommendations} full video scripts including: HOOK (0-3s), INTRO (3-10s), MAIN CONTENT, and CTA."
    elif content_type == "hooks":
        task = f"Generate exactly {num_recommendations} powerful opening hooks under 12 words each."
    elif content_type == "cta":
        task = f"Generate exactly {num_recommendations} strong call-to-action statements."
    else:
        task = f"Generate exactly {num_recommendations} high-quality social media posts."

    return f"""{task}

- Topic: {topic}
- Platform: {platform.upper()}
- Tone: {tone}
- Target Audience: {audience}{context_block}

Output only the content requested."""