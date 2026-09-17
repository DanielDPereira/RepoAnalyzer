import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.pipeline import Analyzer


def test_normalize_github_url_accepts_plain_repo_urls():
    assert Analyzer._normalize_github_url("https://github.com/user/repo") == \
        "https://github.com/user/repo"
    assert Analyzer._normalize_github_url("https://github.com/user/repo/") == \
        "https://github.com/user/repo"
    assert Analyzer._normalize_github_url("http://www.github.com/user/repo") == \
        "https://github.com/user/repo"


def test_normalize_github_url_strips_git_suffix_query_and_fragment():
    assert Analyzer._normalize_github_url("https://github.com/user/repo.git") == \
        "https://github.com/user/repo"
    assert Analyzer._normalize_github_url("https://github.com/user/repo?tab=readme") == \
        "https://github.com/user/repo"
    assert Analyzer._normalize_github_url("https://github.com/user/repo#readme") == \
        "https://github.com/user/repo"


def test_normalize_github_url_rejects_non_repo_or_other_hosts():
    assert Analyzer._normalize_github_url("https://gitlab.com/user/repo") is None
    assert Analyzer._normalize_github_url("not a url") is None
    assert Analyzer._normalize_github_url("https://github.com/user") is None
    assert Analyzer._normalize_github_url("") is None


def test_chunks_splits_by_max_chars():
    text = "\n".join(f"line {i}" for i in range(100))
    chunks = Analyzer._chunks(text, max_chars=50)
    assert len(chunks) > 1
    assert all(len(c) <= 60 for c in chunks)  # small tolerance for line boundaries


def test_chunks_returns_placeholder_for_empty_file():
    assert Analyzer._chunks("", max_chars=100) == ["[arquivo vazio]"]


def test_budget_summaries_keeps_at_least_one_even_if_oversized():
    summaries = ["a" * 1000]
    selected, omitted = Analyzer._budget_summaries(summaries, max_chars=10)
    assert selected == summaries
    assert omitted == 0


def test_budget_summaries_drops_overflow_and_reports_count():
    summaries = ["a" * 100, "b" * 100, "c" * 100]
    selected, omitted = Analyzer._budget_summaries(summaries, max_chars=150)
    assert selected == ["a" * 100]
    assert omitted == 2


def test_budget_summaries_noop_when_no_limit():
    summaries = ["a", "b", "c"]
    selected, omitted = Analyzer._budget_summaries(summaries, max_chars=0)
    assert selected == summaries
    assert omitted == 0


def test_estimate_llm_calls_single_chunk_file_costs_one_call():
    settings = Settings(max_chunk_chars=1000, workspace_dir=Path("/tmp/ri-test-ws"))
    analyzer = Analyzer(settings)
    files = [SimpleNamespace(size=100)]
    # 1 arquivo cabendo em 1 bloco (1 chamada) + 1 chamada de síntese final.
    assert analyzer._estimate_llm_calls(files) == 2


def test_estimate_llm_calls_multi_chunk_file_adds_synthesis_call():
    settings = Settings(max_chunk_chars=100, workspace_dir=Path("/tmp/ri-test-ws"))
    analyzer = Analyzer(settings)
    files = [SimpleNamespace(size=250)]  # 3 blocos estimados
    # 3 chamadas de bloco + 1 de síntese do arquivo + 1 de síntese final.
    assert analyzer._estimate_llm_calls(files) == 5


def test_estimate_llm_calls_empty_file_counts_as_one_chunk():
    settings = Settings(max_chunk_chars=100, workspace_dir=Path("/tmp/ri-test-ws"))
    analyzer = Analyzer(settings)
    files = [SimpleNamespace(size=0)]
    assert analyzer._estimate_llm_calls(files) == 2


def test_persisted_run_loaded_from_disk(tmp_path):
    report_dir = tmp_path / "reports" / "testrun123"
    report_dir.mkdir(parents=True)
    (report_dir / "report.md").write_text("# Test Report", encoding="utf-8")
    (report_dir / "inventory.json").write_text('{"url": "https://github.com/foo/bar", "total_files": 5}', encoding="utf-8")

    settings = Settings(workspace_dir=tmp_path)
    analyzer = Analyzer(settings)

    # Não está em self.runs inicialmente
    assert "testrun123" not in analyzer.runs

    # Status carrega do disco
    status = analyzer.status("testrun123")
    assert status["run_id"] == "testrun123"
    assert status["status"] == "completed"
    assert status["url"] == "https://github.com/foo/bar"

    # Report lê do disco
    assert analyzer.report("testrun123") == "# Test Report"

    # list_runs inclui o item persistido
    runs = analyzer.list_runs()
    assert any(r["run_id"] == "testrun123" for r in runs)


