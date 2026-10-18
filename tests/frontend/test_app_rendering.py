"""Run the complete Streamlit script with synthetic backend responses."""

from pathlib import Path
from types import SimpleNamespace

import pytest
import requests_mock
from streamlit.testing.v1 import AppTest


@pytest.fixture(autouse=True)
def mock_streamlit():
    # Override the global helper mocks: this module must exercise real rendering.
    yield


def test_complete_conversation_renders_native_messages_and_translation(monkeypatch):
    monkeypatch.setenv('BACKEND_SERVER', 'http://synthetic-backend.invalid')
    app_file = Path(__file__).resolve().parents[2] / 'frontend' / 'app.py'
    exchange = dict(response1='Synthetic original A', response2='Synthetic original B',
                    translate1='Synthetic English A', translate2='Synthetic English B')
    import src.utils as utils
    monkeypatch.setattr(utils, 'time', SimpleNamespace(sleep=lambda _: None))
    with requests_mock.Mocker() as backend:
        backend.post('http://synthetic-backend.invalid/reset_conversation', json={})
        backend.post('http://synthetic-backend.invalid/generate_conversation', json=exchange)
        backend.post('http://synthetic-backend.invalid/generate_summary', json={'summary': 'Synthetic learning points'})
        app = AppTest.from_file(str(app_file), default_timeout=15).run()
        assert not app.exception
        app.sidebar.button[0].click().run()
        assert not app.exception
        assert len(app.chat_message) == 8
        assert not app.get('component_instance')
        assert app.session_state['summary'] == 'Synthetic learning points'
        next(button for button in app.button if button.label == 'Translate to English').click().run()
        assert not app.exception
        rendered = [element.value for element in app.markdown]
        assert 'Synthetic English A' in rendered and 'Synthetic English B' in rendered
        session_ids = {request.headers['X-Session-ID'] for request in backend.request_history}
        assert len(session_ids) == 1
        app.sidebar.text_input[4].set_value('Changed synthetic scenario').run()
        assert not app.exception
        assert len(app.chat_message) == 8
        assert 'Changed synthetic scenario' not in '\n'.join(element.value for element in app.markdown)
        assert app.info[0].value == 'Settings changed. Select Generate to start a new conversation.'
