"""Synthetic API regression tests; no model server or outbound calls."""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from backend import app as api

PAYLOAD = {
    "engine": "OpenAI", "role_dict": {"role1": {"name": "Customer"}, "role2": {"name": "Waiter"}},
    "language": "English", "scenario": "at a cafe", "proficiency_level": "Beginner",
    "learning_mode": "Conversation", "session_length": "Short",
}
A = {"X-Session-ID": "a" * 32}
B = {"X-Session-ID": "b" * 32}


@pytest.fixture
def client(monkeypatch):
    api._sessions.clear()
    factory = MagicMock()
    factory.side_effect = lambda **kwargs: MagicMock(
        step=MagicMock(return_value=("Hello", "Hi", "Hello", "Hi")),
        summary=MagicMock(return_value="Learning points"),
    )
    monkeypatch.setattr(api, "DualChatbot", factory)
    with TestClient(api.app) as client:
        yield client, factory
    api._sessions.clear()


def test_missing_summary_preserves_400(client):
    c, _ = client
    assert c.post("/generate_summary", json=PAYLOAD).status_code == 400


def test_sessions_have_separate_history_and_resets(client):
    c, factory = client
    for headers in (A, B, A):
        assert c.post("/generate_conversation", json=PAYLOAD, headers=headers).status_code == 200
    assert factory.call_count == 2
    assert api._sessions[A["X-Session-ID"]][0].step.call_count == 2
    c.post("/reset_conversation", headers=A)
    assert c.post("/generate_summary", json=PAYLOAD, headers=A).status_code == 400
    assert c.post("/generate_summary", json=PAYLOAD, headers=B).json() == {"summary": "Learning points"}


def test_changed_settings_start_a_new_conversation(client):
    c, factory = client
    c.post("/generate_conversation", json=PAYLOAD, headers=A)
    changed = dict(PAYLOAD, language="Spanish")
    assert c.post("/generate_summary", json=changed, headers=A).status_code == 409
    assert c.post("/generate_conversation", json=changed, headers=A).status_code == 200
    assert factory.call_count == 2


def test_model_errors_do_not_expose_internal_details(client):
    c, factory = client
    factory.side_effect = RuntimeError("private synthetic server detail")
    response = c.post("/generate_conversation", json=PAYLOAD, headers=A)
    assert response.status_code == 502
    assert "private synthetic" not in response.text
    assert not api._sessions


def test_validation_and_capacity(client, monkeypatch):
    c, _ = client
    assert c.post("/generate_conversation", json=dict(PAYLOAD, language="invalid")).status_code == 422
    assert c.post("/generate_conversation", json=dict(PAYLOAD, role_dict={})).status_code == 422
    assert c.post("/generate_conversation", json=PAYLOAD, headers={"X-Session-ID": "short"}).status_code == 422
    monkeypatch.setattr(api, "MAX_SESSIONS", 1)
    assert c.post("/generate_conversation", json=PAYLOAD, headers=A).status_code == 200
    assert c.post("/generate_conversation", json=PAYLOAD, headers=B).status_code == 429
    monkeypatch.setattr(api, "SESSION_TTL", -1)
    assert c.post("/generate_conversation", json=PAYLOAD, headers=B).status_code == 200


def test_legacy_no_header_client_still_works(client):
    c, _ = client
    assert c.post("/generate_conversation", json=PAYLOAD).status_code == 200
    assert c.post("/generate_summary", json=PAYLOAD).status_code == 200
    assert c.post("/reset_conversation").status_code == 200


def test_busy_inference_returns_503_without_waiting_for_a_model(client, monkeypatch):
    c, factory = client
    lock = MagicMock()
    lock.acquire.return_value = False
    monkeypatch.setattr(api, '_lock', lock)
    assert c.post('/generate_conversation', json=PAYLOAD, headers=A).status_code == 503
    lock.acquire.assert_called_once_with(timeout=5)
    factory.assert_not_called()
