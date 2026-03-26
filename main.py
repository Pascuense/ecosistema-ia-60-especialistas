import os
import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any

app = FastAPI(title="Ecosistema IA - 60 Especialistas")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no configurada")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client

class ChatRequest(BaseModel):
    messages: list[Any]
    system: Optional[str] = ""
    max_tokens: int = 800
    model: str = "claude-haiku-4-5-20251001"

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        client = get_client()
        kwargs = dict(model=req.model, max_tokens=min(req.max_tokens, 2000), messages=req.messages)
        if req.system:
            kwargs["system"] = req.system
        response = client.messages.create(**kwargs)
        return {"text": response.content[0].text}
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="API key invalida")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok", "api_key_configured": bool(os.environ.get("ANTHROPIC_API_KEY"))}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
rtidos de 
