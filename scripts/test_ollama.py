import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.ollama_client import OllamaClient

client = OllamaClient(
    settings.ollama_base_url,
    settings.ollama_model,
    settings.request_timeout_seconds,
    settings.ollama_keep_alive,
)

client.check()
print(f"Ollama OK: {settings.ollama_model}")
print(client.chat(
    "Você é um teste de infraestrutura. Seja breve.",
    "Responda apenas: Repository Intelligence OK"
))
