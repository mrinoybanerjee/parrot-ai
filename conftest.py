"""
This module is used to add the project root and component roots to the Python path,
as well as to define fixtures for mocking LLM and backend servers.
"""

import requests_mock
import pytest
import sys
import os
from unittest import mock

# Get the absolute path of the project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to the Python path
sys.path.insert(0, project_root)

# Add backend and frontend directories to the Python path
backend_path = os.path.join(project_root, 'backend')
frontend_path = os.path.join(project_root, 'frontend')

sys.path.insert(0, backend_path)
sys.path.insert(0, frontend_path)

class SessionStateMock(dict):
    """
    A mock class to simulate Streamlit's session state using a dictionary.
    """
    def __getattr__(self, item):
        return self[item]
    
    def __setattr__(self, key, value):
        self[key] = value

@pytest.fixture(scope="session")
def mock_llm_server():
    """
    A pytest fixture to mock the LLM server.

    Mocks the endpoint for generating chat completions and the Google Translate API.

    Yields:
        requests_mock.Mocker: The mocked LLM server.
    """
    with requests_mock.Mocker() as m:
        m.post('http://localhost:8080/v1/chat/completions', json={
            'choices': [{'message': {'content': 'Mocked LLM response'}}]
        })
        # Mock Google Translate API
        m.post('https://translate.google.com/_/TranslateWebserverUi/data/batchexecute', text='')
        yield m

@pytest.fixture(scope="session")
def mock_backend_server():
    """
    A pytest fixture to mock the backend server.

    Mocks the endpoints for generating conversation, generating summary, and resetting conversation.

    Yields:
        requests_mock.Mocker: The mocked backend server.
    """
    with requests_mock.Mocker() as m:
        m.post('http://localhost:8000/generate_conversation', json={
            "response1": "Hello",
            "response2": "Hi there",
            "translate1": "Hello",
            "translate2": "Hi there"
        })
        m.post('http://backend:8000/generate_conversation', json={
            "response1": "Hello",
            "response2": "Hi there",
            "translate1": "Hello",
            "translate2": "Hi there"
        })
        m.post('http://localhost:8000/generate_summary', json={
            "summary": "This is a summary"
        })
        m.post('http://backend:8000/generate_summary', json={
            "summary": "This is a summary"
        })
        m.post('http://localhost:8000/reset_conversation', status_code=200)
        m.post('http://backend:8000/reset_conversation', status_code=200)
        yield m

@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """
    A pytest fixture to mock Streamlit components and session state.

    Ensures BACKEND_SERVER is set to the correct URL and mocks Streamlit components and session state.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object for modifying environment variables.

    Yields:
        tuple: The mocked container, column, and session state.
    """
    # Ensure BACKEND_SERVER is set to the correct URL
    monkeypatch.setenv("BACKEND_SERVER", "http://localhost:8000")

    with mock.patch('streamlit.container') as mock_container:
        with mock.patch('streamlit.columns') as mock_columns:
            mock_column = mock.MagicMock()
            mock_columns.return_value = [mock_column, mock_column, mock_column]
            # Use SessionStateMock for session_state
            with mock.patch('streamlit.session_state', new_callable=SessionStateMock) as mock_session_state:
                yield mock_container, mock_column, mock_session_state
