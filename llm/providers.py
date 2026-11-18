"""LLM provider setup from .env, shared by the check-in classifier and api/review_arabic.py.

One small function per call: `chat(messages) -> reply text`. Stdlib only (urllib), no SDK. Providers, picked by
LLM_PROVIDER: "groq" (GROQ_API_KEY, GROQ_MODEL), "openai" (OPENAI_API_KEY, OPENAI_MODEL) and "azure"
(AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT). All three speak the OpenAI chat format."""

import json
import os
import urllib.request
from collections.abc import Callable

AZURE_API_VERSION = "2024-10-21"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
USER_AGENT = "rebound-api/0.1"

Messages = list[dict[str, str]]
Chat = Callable[[Messages], str]


def _endpoint() -> tuple[str, str, dict[str, str], dict[str, str]] | None:
    """(name, url, headers, extra body fields) for the configured provider, or None if it isn't fully set up."""
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    env = os.environ
    if provider == "groq" and env.get("GROQ_API_KEY") and env.get("GROQ_MODEL"):
        return "groq", GROQ_URL, {"Authorization": f"Bearer {env['GROQ_API_KEY']}"}, {"model": env["GROQ_MODEL"]}
    if provider == "openai" and env.get("OPENAI_API_KEY") and env.get("OPENAI_MODEL"):
        return "openai", OPENAI_URL, {"Authorization": f"Bearer {env['OPENAI_API_KEY']}"}, {"model": env["OPENAI_MODEL"]}
    if provider == "azure" and all(env.get(k) for k in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
                                                        "AZURE_OPENAI_DEPLOYMENT")):
        url = (f"{env['AZURE_OPENAI_ENDPOINT'].rstrip('/')}/openai/deployments/"
               f"{env['AZURE_OPENAI_DEPLOYMENT']}/chat/completions?api-version={AZURE_API_VERSION}")
        return "azure", url, {"api-key": env["AZURE_OPENAI_API_KEY"]}, {}
    return None


def provider_name() -> str | None:
    """"groq" | "openai" | "azure", or None when no provider is fully configured."""
    found = _endpoint()
    return found[0] if found else None


def chat_from_env(timeout: float, json_mode: bool = False) -> Chat | None:
    """A chat function for the configured provider, or None without a key. Temperature 0.

    The returned function raises on any network error, timeout, HTTP error or odd reply; callers fall back."""
    found = _endpoint()
    if found is None:
        return None
    _, url, headers, extra = found

    def chat(messages: Messages) -> str:
        body: dict[str, object] = {**extra, "temperature": 0, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        # A User-Agent is required: Groq's firewall rejects urllib's default one (403, Cloudflare error 1010).
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={**headers, "Content-Type": "application/json",
                                              "User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return str(json.load(r)["choices"][0]["message"]["content"]).strip()

    return chat
