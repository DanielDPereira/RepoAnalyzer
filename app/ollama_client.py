import re
import time

import httpx

THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: int,
        keep_alive: str,
        think: bool = False,
        max_retries: int = 2,
        retry_backoff_seconds: float = 3.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.keep_alive = keep_alive
        self.think = think
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = retry_backoff_seconds
        # Um único cliente HTTP é reaproveitado por todas as chamadas
        # (pool de conexões com keep-alive), em vez de abrir e fechar uma
        # conexão TCP nova a cada requisição. httpx.Client é seguro para
        # uso concorrente entre threads.
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def chat(self, system: str, user: str, temperature: float = 0.1) -> str:
        # Quando think está desativado (padrão), garante a tag /nothink no
        # system prompt para modelos que a utilizam (como Qwen3/DeepSeek).
        if not self.think and not system.strip().startswith(("/nothink", "/no_think")):
            system = f"/nothink\n{system}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "keep_alive": self.keep_alive,
            # Modelos com modo de raciocínio (ex.: Qwen3) ficam com "thinking"
            # ligado por padrão no Ollama. Desligamos para manter o relatório
            # limpo; se a versão instalada do Ollama ignorar o parâmetro, o
            # bloco <think>...</think> é removido como salvaguarda abaixo.
            "think": self.think,
            "options": {
                "temperature": temperature
            }
        }

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                break
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_seconds * (attempt + 1))
                    continue
                raise OllamaError(
                    f"Não foi possível acessar o Ollama em {self.base_url} "
                    f"após {self.max_retries + 1} tentativa(s): {last_error}"
                ) from last_error

        content = data.get("message", {}).get("content", "")
        content = THINK_BLOCK_RE.sub("", content).strip()
        if not content:
            raise OllamaError("O Ollama retornou uma resposta vazia.")
        return content

    def check(self) -> None:
        try:
            response = self._client.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Ollama não está acessível em {self.base_url}: {exc}"
            ) from exc

        names = set()
        for item in models:
            for key in ("name", "model"):
                value = item.get(key)
                if value:
                    names.add(value)

        # Aceita correspondência exata ou por tag (ex.: "qwen3:4b" cobre
        # variações onde o Ollama retorna só o nome base ou com ":latest").
        base = self.model.split(":")[0]
        if self.model not in names and not any(n.split(":")[0] == base for n in names):
            raise OllamaError(
                f"Modelo '{self.model}' não está instalado. "
                f"Execute: ollama pull {self.model}"
            )
