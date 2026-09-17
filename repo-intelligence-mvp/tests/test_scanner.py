import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.scanner import detect_language, is_probably_binary, python_symbols, scan_repository


def test_detect_language_by_extension():
    assert detect_language(Path("app/main.py")) == "Python"
    assert detect_language(Path("index.ts")) == "TypeScript"
    assert detect_language(Path("Dockerfile")) == "Dockerfile"
    assert detect_language(Path("unknown.xyz")) == "Unknown"


def test_python_symbols_extracts_functions_and_classes():
    code = """
import os
from pathlib import Path

class Foo:
    def bar(self):
        pass

def baz():
    pass
"""
    result = python_symbols(code)
    # ast.walk() traverses breadth-first, so don't assert a specific order.
    assert {f["name"] for f in result["functions"]} == {"bar", "baz"}
    assert [c["name"] for c in result["classes"]] == ["Foo"]
    assert "os" in result["imports"]
    assert any(imp.startswith("pathlib:") for imp in result["imports"])


def test_python_symbols_handles_syntax_error_gracefully():
    result = python_symbols("def broken(:\n")
    assert "parse_error" in result
    assert result["functions"] == []


def test_is_probably_binary_detects_null_bytes(tmp_path):
    binary_file = tmp_path / "data.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03")
    assert is_probably_binary(binary_file) is True


def test_is_probably_binary_false_for_text(tmp_path):
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello world", encoding="utf-8")
    assert is_probably_binary(text_file) is False


def test_is_probably_binary_by_extension(tmp_path):
    fake_png = tmp_path / "image.png"
    fake_png.write_text("not really binary content", encoding="utf-8")
    assert is_probably_binary(fake_png) is True


def test_scan_repository_ignores_configured_dirs_and_respects_limits(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def run():\n    pass\n", encoding="utf-8")

    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "lib.js").write_text("module.exports = {};", encoding="utf-8")

    (tmp_path / "big.txt").write_text("x" * 1000, encoding="utf-8")

    result = scan_repository(tmp_path, max_file_size=500, max_files=100)

    paths = {item.path for item in result["files"]}
    assert "src/main.py" in paths
    assert not any(p.startswith("node_modules/") for p in paths)

    ignored_reasons = {item["path"]: item["reason"] for item in result["ignored"]}
    assert ignored_reasons.get("big.txt") == "file_too_large"


def test_scan_repository_respects_max_files(tmp_path):
    for i in range(5):
        (tmp_path / f"file_{i}.py").write_text("x = 1\n", encoding="utf-8")

    result = scan_repository(tmp_path, max_file_size=1024, max_files=2)

    assert result["total_files"] == 2
    reasons = {item["reason"] for item in result["ignored"]}
    assert "max_files_reached" in reasons
