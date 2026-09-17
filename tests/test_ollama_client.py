import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ollama_client import OllamaClient


def test_ollama_client_forces_nothink_when_think_is_false():
    client = OllamaClient(
        base_url="http://127.0.0.1:11434",
        model="qwen3:4b",
        timeout=30,
        keep_alive="5m",
        think=False,
    )

    with patch.object(client._client, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"content": "OK"}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        res = client.chat(system="Instrução do sistema", user="Pergunta")

        assert res == "OK"
        called_json = mock_post.call_args[1]["json"]
        assert called_json["think"] is False
        system_msg = next(m["content"] for m in called_json["messages"] if m["role"] == "system")
        assert system_msg.startswith("/nothink\n")


def test_ollama_client_does_not_duplicate_nothink():
    client = OllamaClient(
        base_url="http://127.0.0.1:11434",
        model="qwen3:4b",
        timeout=30,
        keep_alive="5m",
        think=False,
    )

    with patch.object(client._client, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"content": "OK"}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client.chat(system="/nothink\nInstrução", user="Pergunta")
        called_json = mock_post.call_args[1]["json"]
        system_msg = next(m["content"] for m in called_json["messages"] if m["role"] == "system")
        assert system_msg.count("/nothink") == 1
