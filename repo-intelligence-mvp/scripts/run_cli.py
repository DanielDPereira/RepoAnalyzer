import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.pipeline import Analyzer

if len(sys.argv) != 2:
    print("Uso: python scripts/run_cli.py https://github.com/usuario/repositorio")
    raise SystemExit(1)

url = sys.argv[1]
analyzer = Analyzer(settings)
run_id = analyzer.start(url)

print(f"Run ID: {run_id}")

while True:
    state = analyzer.status(run_id)
    print(
        f"[{state['status']}] {state['stage']} - {state['message']}",
        flush=True
    )

    if state["status"] in {"completed", "failed"}:
        break

    time.sleep(2)

if state["status"] == "completed":
    print(f"\nRelatório: {state['report_path']}")
else:
    print(f"\nErro: {state['error']}")
