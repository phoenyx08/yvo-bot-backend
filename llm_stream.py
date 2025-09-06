import httpx
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
OLLAMA_URL = os.getenv("OLLAMA_URL")

async def ollama_stream(history: list[dict]) -> AsyncGenerator[bytes, None]:
    """
    Async generator that yields raw bytes from Ollama as soon as they arrive.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": history,
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk
