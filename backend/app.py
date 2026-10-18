"""Local conversation API. State is scoped to an optional client session header."""

import logging
import os
import threading
import time
from contextlib import contextmanager
from typing import Dict, Literal, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

try:  # support both `uvicorn backend.app:app` and the backend Docker image
    from .src.chatbot import DualChatbot
except ImportError:
    from src.chatbot import DualChatbot

app = FastAPI()
LLM_SERVER = os.environ.get("LLM_SERVER", "http://localhost:8080")
logger = logging.getLogger(__name__)
MAX_SESSIONS = 128
SESSION_TTL = 3600
# Local inference is serialized: a reset cannot race a step or summary. Sync
# endpoints run in FastAPI's worker pool rather than blocking its event loop.
_lock = threading.Lock()
_sessions = {}


class Role(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    action: str = Field(default="", max_length=1000)


class ConversationRequest(BaseModel):
    engine: Literal["OpenAI"]
    role_dict: Dict[Literal["role1", "role2"], Role]
    language: Literal["English", "Hindi", "German", "Spanish", "French"]
    scenario: str = Field(min_length=1, max_length=4000)
    proficiency_level: Literal["Beginner", "Intermediate", "Advanced"]
    learning_mode: Literal["Conversation", "Debate"]
    session_length: Literal["Short", "Long"]


class ConversationResponse(BaseModel):
    response1: str
    response2: str
    translate1: str
    translate2: str


@contextmanager
def inference_slot():
    if not _lock.acquire(timeout=5):
        raise HTTPException(status_code=503, detail="The local model is busy. Try again shortly.")
    try:
        yield
    finally:
        _lock.release()


def session_header(x_session_id: Optional[str]) -> str:
    # No-header clients retain the original single-session API behavior.
    return x_session_id or "legacy"


def prune_sessions():
    cutoff = time.monotonic() - SESSION_TTL
    for key in list(_sessions):
        if _sessions[key][2] < cutoff:
            del _sessions[key]


def request_config(request):
    config = request.model_dump()
    if set(config["role_dict"]) != {"role1", "role2"}:
        raise HTTPException(status_code=422, detail="Provide role1 and role2.")
    return config


@app.post("/generate_conversation", response_model=ConversationResponse)
def generate_conversation(
    request: ConversationRequest,
    x_session_id: Optional[str] = Header(default=None, min_length=16, max_length=64, pattern=r"^[a-zA-Z0-9-]+$"),
):
    config = request_config(request)
    key = session_header(x_session_id)
    with inference_slot():
        prune_sessions()
        current = _sessions.get(key)
        if current is None and len(_sessions) >= MAX_SESSIONS:
            raise HTTPException(status_code=429, detail="Too many active sessions. Try again later.")
        try:
            if current is None or current[1] != config:
                bot = DualChatbot(**request.model_dump(), llm_server=LLM_SERVER)
            else:
                bot = current[0]
            response1, response2, translate1, translate2 = bot.step()
            _sessions[key] = (bot, config, time.monotonic())
            return ConversationResponse(response1=response1, response2=response2,
                                        translate1=translate1, translate2=translate2)
        except Exception:
            # A partial step must not be silently continued on retry.
            _sessions.pop(key, None)
            logger.error("Conversation generation failed")
            raise HTTPException(status_code=502, detail="The local model could not generate a conversation. Check the model server and retry.") from None


@app.post("/generate_summary")
def generate_summary(
    request: ConversationRequest,
    x_session_id: Optional[str] = Header(default=None, min_length=16, max_length=64, pattern=r"^[a-zA-Z0-9-]+$"),
):
    config = request_config(request)
    with inference_slot():
        prune_sessions()
        key = session_header(x_session_id)
        current = _sessions.get(key)
        if current is None:
            raise HTTPException(status_code=400, detail="No conversation has been generated yet.")
        if current[1] != config:
            raise HTTPException(status_code=409, detail="Settings changed. Generate a new conversation first.")
        try:
            summary = current[0].summary()
        except Exception:
            logger.error("Summary generation failed")
            raise HTTPException(status_code=502, detail="The local model could not generate a summary. Try again.") from None
        _sessions[key] = (current[0], current[1], time.monotonic())
        return {"summary": summary}


@app.post("/reset_conversation")
def reset_conversation(
    x_session_id: Optional[str] = Header(default=None, min_length=16, max_length=64, pattern=r"^[a-zA-Z0-9-]+$"),
):
    with inference_slot():
        _sessions.pop(session_header(x_session_id), None)
    return {"message": "Conversation reset successfully"}


@app.get("/")
def root():
    return {"message": "Parrot-AI backend is running"}
