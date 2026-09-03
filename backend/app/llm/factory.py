"""Factory for creating the configured LLM interpreter."""

import logging
from app.core.config import Settings
from app.llm.adapter import CloudLLMInterpreter
from app.llm.base import Interpreter
from app.llm.mock import MockInterpreter

logger = logging.getLogger(__name__)


def get_interpreter(settings: Settings) -> Interpreter:
    """Return configured Interpreter instance.

    Uses CloudLLMInterpreter if LLM_API_KEY is configured.
    Otherwise falls back to MockInterpreter for local development and tests.
    """
    if settings.LLM_API_KEY and settings.LLM_API_KEY.strip():
        logger.info(f"Initializing CloudLLMInterpreter with model: {settings.LLM_MODEL or 'default'}")
        return CloudLLMInterpreter(
            api_key=settings.LLM_API_KEY.strip(),
            model=settings.LLM_MODEL or "gpt-4o-mini",
            base_url=settings.LLM_BASE_URL or "https://api.openai.com/v1",
        )

    logger.info("Initializing MockInterpreter (no LLM_API_KEY configured)")
    return MockInterpreter()
