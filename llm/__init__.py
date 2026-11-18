"""LLM layer (TASK_01_C, lean): classify check-in free text into a Barrier, plus an optional red-flag second check.

The app works fully without it: api/llm_client.py falls back to keywords when no provider is configured or a call
fails. See llm/README.md."""

from .classifier import MIN_CONFIDENCE, TIMEOUT_S, check_red_flag, classify_barrier
from .providers import chat_from_env, provider_name

__all__ = ["MIN_CONFIDENCE", "TIMEOUT_S", "chat_from_env", "check_red_flag", "classify_barrier", "provider_name"]
