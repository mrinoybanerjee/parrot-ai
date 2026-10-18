# Synthetic API check — October 18, 2026

This checks application behavior with fixed synthetic outputs. It does not
measure model inference, language quality, learner outcomes or production capacity.

## Reproduce

From the repository root, use Python 3.12 and the test dependencies from the README:

```sh
python scripts/benchmark_local.py --output /tmp/parrot-synthetic-api.json
```

The script starts an ephemeral fake OpenAI-compatible HTTP server on `127.0.0.1`.
FastAPI TestClient calls the real endpoints in process. The real OpenAI SDK calls
only that loopback fake server. No model, audio, browser, credentials or external
services are used. The SDK uses the application's existing dummy local key.

## Workload and result

Each concurrency level runs ten unique synthetic sessions for two turns each.
Settings are German, Beginner, Conversation and Short. Each turn makes four SDK
calls, including translations. Fixed fake responses have no deliberate delay.
The first turn creates clients; the second continues each session. Timings mix
those two paths. A separate summary and reset checks each session.

| Concurrent clients | HTTP 200 | Unexpected output | p50 ms | p95 ms |
|---|---:|---:|---:|---:|
| 1 | 20/20 | 0 | 3.72 | 4.43 |
| 2 | 20/20 | 0 | 7.03 | 8.10 |
| 5 | 20/20 | 0 | 17.20 | 27.57 |

The script observed 275 fake-model requests and zero missing/mixed session
markers. All 30 summary/reset checks passed. An injected model HTTP 500 produced
API HTTP 502 without exposing its error text; a retry returned 200. Holding the
inference lock produced HTTP 503 after 5.01 seconds.

These timings exclude the browser and Streamlit-to-FastAPI network hop. They
include framework scheduling, SDK calls and loopback fake-server response time.
Twenty samples per concurrency are too few for a capacity claim. p95 uses the
nearest-rank method; timing is informational and has no performance threshold.
The marker check covers this fixture, not every possible isolation failure.

## Environment and receipts

Apple M4, 16 GiB RAM, macOS 26.6.2 (Darwin 25.6.0), arm64; Python 3.12.12.
The raw [JSON receipt](synthetic-api-20261018.json) records the exact OS string,
package versions, source hashes and every timed generation request. It identifies
base commit `03dbb8e4b60c9245f32a56c79746a2b8e555c05c` plus the local benchmark/documentation changes.
Application source was unchanged from that commit. Source hashes identify the
exact benchmark implementation even though it was not committed at run time.

The original [historical experiment](../EVALUATION_RESULTS.md) remains separate.
Its model timings are not comparable with this fake-server fixture.
