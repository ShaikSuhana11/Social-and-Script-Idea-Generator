"""Groq LLM API integration with error handling."""

import os
from typing import Optional
from groq import Groq, GroqError
from dotenv import load_dotenv

load_dotenv()

# SECURE: Loads from Render Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Changed to a model that Groq actually supports
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")


class LLMServiceError(Exception):
    """Custom exception for LLM service failures."""
    pass


class LLMService:
    """Wrapper around Groq API for text generation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        if not self.api_key:
            raise LLMServiceError("GROQ_API_KEY not set in environment.")
        self.client = Groq(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        """Generate text from Groq API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {}
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            if not content:
                finish_reason = response.choices[0].finish_reason
                raise LLMServiceError(f"Model returned empty content. Finish reason: {finish_reason}")
                
            return content.strip()

        except GroqError as e:
            # This prints the real error to Render logs
            print(f"REAL GROQ ERROR: {repr(e)}")
            raise LLMServiceError(f"Groq API error: {str(e)}") from e
        except Exception as e:
            print(f"REAL LLM ERROR: {repr(e)}")
            raise LLMServiceError(f"Unexpected LLM error: {str(e)}") from e


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
