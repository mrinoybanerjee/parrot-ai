"""Synthetic API/SDK benchmark. Only an ephemeral loopback fake model is used."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import hashlib
from importlib.metadata import version
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import threading
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend import app as api


class FakeModel(BaseHTTPRequestHandler):
    """Exercise the real OpenAI client without downloading or invoking a model."""

    fail_next = False
    invalid_contexts = 0
    calls = 0

    def log_message(self, *args):
        pass

    def do_POST(self):
        assert self.path == "/v1/chat/completions"
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        markers = set(re.findall(r"fixture-[0-9]+-[0-9]+", json.dumps(payload["messages"])))
        type(self).calls += 1
        if len(markers) != 1:
            type(self).invalid_contexts += 1
        if type(self).fail_next:
            type(self).fail_next = False
            status, body = 500, {"error": {"message": "synthetic failure", "type": "test"}}
        else:
            status = 200
            body = {"id": "synthetic", "object": "chat.completion", "created": 0,
                    "model": "fake-fixed-response", "choices": [{"index": 0,
                    "message": {"role": "assistant", "content": "Synthetic " + ",".join(sorted(markers))},
                    "finish_reason": "stop"}]}
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def payload(marker):
    return {"engine": "OpenAI", "role_dict": {"role1": {"name": "Customer"},
            "role2": {"name": "Barista"}}, "language": "German", "scenario": marker,
            "proficiency_level": "Beginner", "learning_mode": "Conversation", "session_length": "Short"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    api._sessions.clear()
    model = ThreadingHTTPServer(("127.0.0.1", 0), FakeModel)
    thread = threading.Thread(target=model.serve_forever, daemon=True)
    thread.start()
    outcomes, levels = [], []
    try:
        # Ignore environment proxies. Every SDK request must use this loopback server.
        with patch.dict(os.environ, {"NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"}), \
                patch.object(api, "LLM_SERVER", f"http://127.0.0.1:{model.server_port}"), \
                TestClient(api.app) as client:
            def generate(item):
                concurrency, index, turn = item
                marker = f"fixture-{concurrency}-{index}"
                headers = {"X-Session-ID": f"synthetic-{concurrency}-{index:016d}"}
                start = time.perf_counter()
                response = client.post("/generate_conversation", json=payload(marker), headers=headers)
                elapsed = (time.perf_counter() - start) * 1000
                valid = response.status_code == 200 and all(
                    value == "Synthetic " + marker for value in response.json().values())
                return {"concurrency": concurrency, "session": index, "turn": turn,
                        "status": response.status_code, "elapsed_ms": elapsed, "expected_output": valid}

            for concurrency in (1, 2, 5):
                rows = []
                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    for turn in (1, 2):
                        rows.extend(executor.map(generate, [(concurrency, i, turn) for i in range(10)]))
                outcomes.extend(rows)
                latencies = sorted(row["elapsed_ms"] for row in rows)
                levels.append({"concurrency": concurrency, "requests": len(rows),
                               "successes": sum(row["status"] == 200 for row in rows),
                               "unexpected_outputs": sum(not row["expected_output"] for row in rows),
                               "p50_ms": (latencies[9] + latencies[10]) / 2,
                               "p95_ms_nearest_rank": latencies[math.ceil(.95 * len(rows)) - 1]})
                for index in range(10):
                    marker = f"fixture-{concurrency}-{index}"
                    headers = {"X-Session-ID": f"synthetic-{concurrency}-{index:016d}"}
                    summary = client.post("/generate_summary", json=payload(marker), headers=headers)
                    assert summary.status_code == 200 and summary.json() == {"summary": "Synthetic " + marker}
                    assert client.post("/reset_conversation", headers=headers).status_code == 200
                assert not api._sessions

            headers = {"X-Session-ID": "synthetic-failure-000000"}
            FakeModel.fail_next = True
            failed = client.post("/generate_conversation", json=payload("fixture-0-0"), headers=headers)
            assert failed.status_code == 502 and "synthetic failure" not in failed.text
            assert not api._sessions
            retried = client.post("/generate_conversation", json=payload("fixture-0-0"), headers=headers)
            assert retried.status_code == 200
            with api._lock:
                start = time.perf_counter()
                busy = client.post("/generate_conversation", json=payload("fixture-0-0"), headers=headers)
                busy_ms = (time.perf_counter() - start) * 1000
            assert busy.status_code == 503
            assert FakeModel.invalid_contexts == 0
            assert all(row["expected_output"] for row in outcomes)
    finally:
        api._sessions.clear()
        model.shutdown()
        model.server_close()
        thread.join()

    result = {"schema": 1, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "worktree_changes": subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines(),
              "environment": {"python": platform.python_version(), "os": platform.platform(),
                              "architecture": platform.machine(), "logical_cpus": os.cpu_count(),
                              "packages": {name: version(name) for name in ("fastapi", "starlette", "httpx", "openai", "pydantic")}},
              "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest()
                                for name in ("backend/app.py", "backend/src/chatbot.py", "scripts/benchmark_local.py")},
              "workload": "ASGI TestClient, real OpenAI SDK, loopback fixed fake model; German/Beginner/Conversation/Short; 10 unique sessions and 2 turns per concurrency; 4 model calls per turn; no deliberate model delay",
              "limitations": "No browser, application network hop, inference, audio, language quality, production capacity or user impact measured. 20 samples per concurrency; timing is informational, no performance gate.",
              "summary": levels, "model_calls": FakeModel.calls,
              "invalid_or_mixed_session_contexts": FakeModel.invalid_contexts,
              "failure_checks": {"injected_model_error_status": failed.status_code,
                                 "retry_status": retried.status_code, "busy_status": busy.status_code,
                                 "busy_elapsed_ms": busy_ms}, "requests": outcomes}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("summary", "model_calls", "invalid_or_mixed_session_contexts", "failure_checks")}, indent=2))


if __name__ == "__main__":
    main()
