
"""Groq LLM API integration with error handling."""

import os
from typing import Optional

from groq import Groq, GroqError
from dotenv import load_dotenv

load_dotenv()

# Load credentials and model from environment variables.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


class LLMServiceError(Exception):
    """Custom exception for LLM service failures."""
    pass


class LLMService:
    """Wrapper around Groq API for text generation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL

        if not self.api_key:
            raise LLMServiceError(
                "GROQ_API_KEY not set in environment."
            )

        self.client = Groq(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: int = 4096,
        reasoning_effort: Optional[str] = "low",
    ) -> str:
        """Generate text from Groq API."""

        if not prompt or not prompt.strip():
            raise LLMServiceError("Prompt cannot be empty.")

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        # Use GPT-OSS-specific settings only for GPT-OSS models.
        is_gpt_oss = self.model.startswith("openai/gpt-oss")

        kwargs = {
            "max_completion_tokens": max_tokens,
        }

        if is_gpt_oss:
            kwargs["include_reasoning"] = False

            if reasoning_effort:
                kwargs["reasoning_effort"] = reasoning_effort

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )

            if not response.choices:
                raise LLMServiceError(
                    "Groq returned no completion choices."
                )

            choice = response.choices[0]
            content = choice.message.content

            if not content or not content.strip():
                finish_reason = choice.finish_reason

                raise LLMServiceError(
                    "Model returned empty content. "
                    f"Finish reason: {finish_reason}. "
                    "Check completion token limits and prompt size."
                )

            return content.strip()

        except LLMServiceError:
            raise

        except GroqError as e:
            print(f"REAL GROQ ERROR: {repr(e)}")
            raise LLMServiceError(
                f"Groq API error: {str(e)}"
            ) from e

        except Exception as e:
            print(f"REAL LLM ERROR: {repr(e)}")
            raise LLMServiceError(
                f"Unexpected LLM error: {str(e)}"
            ) from e


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService()

    return _llm_service
