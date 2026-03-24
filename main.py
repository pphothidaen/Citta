from fastapi import FastAPI, HTTPException, Request
from litellm import completion
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Citta Proxy Gateway - IDE Compatible")

ORCHESTRATOR_CODE_DIRECTIVE = """
You are the core intelligence of 'The Citta' accessed via an IDE coding agent.
STRICT RULES:
1. NO FLATTERY, NO FLUFF. Omit greetings, pleasantries, and concluding remarks.
2. If providing architectural advice, enforce this structure:
   - Positives (Pros)
   - Negatives (Cons / Blind spots)
   - Engineering Trade-offs
3. If writing code: Output production-ready code immediately. Follow ZERO-WASTE principles (optimize compute, minimize latency).
4. Maintain absolute objectivity.
"""


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "service": "gateway-proxy"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        original_messages = body.get("messages", [])

        # Inject a single authoritative system directive before user/assistant turns.
        system_injection = [{"role": "system", "content": ORCHESTRATOR_CODE_DIRECTIVE}]
        modified_messages = system_injection + [
            msg for msg in original_messages if msg.get("role") != "system"
        ]

        requested_model = body.get("model", "deepseek-chat")
        model_aliases = {
            "gemini/gemini-1.5-pro": "gemini/gemini-2.0-flash",
            "gemini-1.5-pro": "gemini/gemini-2.0-flash",
            # LiteLLM 1.22.x handles DeepSeek reliably through OpenAI-compatible routing.
            "deepseek-chat": "openai/deepseek-chat",
            "deepseek/deepseek-chat": "openai/deepseek-chat",
            "deepseek-reasoner": "openai/deepseek-reasoner",
            "deepseek/deepseek-reasoner": "openai/deepseek-reasoner",
        }
        target_model = model_aliases.get(requested_model, requested_model)

        completion_kwargs = {
            "model": target_model,
            "messages": modified_messages,
            "temperature": body.get("temperature", 0.1),
            "stream": body.get("stream", False),
        }

        if target_model.startswith("openai/deepseek-"):
            completion_kwargs["api_base"] = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
            completion_kwargs["api_key"] = os.getenv("DEEPSEEK_API_KEY", "")

        response = completion(**completion_kwargs)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
