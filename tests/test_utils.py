"""Tests for the utility functions."""

from unittest.mock import Mock, patch
import pytest
from src.utils import initialize_session_state, show_messages

@pytest.fixture
def mock_st():
    """Mock the Streamlit session state."""
    with patch('src.utils.st') as mock:
        mock.session_state = {}
        yield mock

@pytest.fixture
def mock_message():
    """Mock the Streamlit message function."""
    with patch('src.utils.message') as mock:
        yield mock

@pytest.fixture
def mock_time():
    """Mock the time.sleep function."""
    with patch('src.utils.time') as mock:
        yield mock

@pytest.fixture
def mock_gtts():
    """Mock the gTTS class."""
    with patch('src.utils.gTTS') as mock:
        yield mock

def test_initialize_session_state(mock_st):
    """
    Test the initialize_session_state function.
    
    Args:
        mock_st (Mock): The mocked Streamlit session state.
    
    Returns:
        None
    """
    initialize_session_state()
    assert "bot1_mesg" in mock_st.session_state
    assert "bot2_mesg" in mock_st.session_state
    assert "batch_flag" in mock_st.session_state
    assert "translate_flag" in mock_st.session_state
    assert "audio_flag" in mock_st.session_state
    assert "message_counter" in mock_st.session_state

def test_show_messages(mock_message, mock_time, mock_gtts, mock_st):
    """
    Test the show_messages function.
    
    Args:
        mock_message (Mock): The mocked Streamlit message function.
        mock_time (Mock): The mocked time.sleep function.
        mock_gtts (Mock): The mocked gTTS class.
        mock_st (Mock): The mocked Streamlit session state.
    
    Returns:
        None
    """
    mesg_1 = {
        "role": "Customer",
        "content": "Hello",
        "translation": "Hola",
        "language": "Spanish"
    }
    mesg_2 = {
        "role": "Waitstaff",
        "content": "How can I help you?",
        "translation": "¿Cómo puedo ayudarte?",
        "language": "Spanish"
    }
    
    new_counter = show_messages(mesg_1, mesg_2, 0, 2, batch=False, audio=True, translation=True)
    
    assert new_counter == 4
    assert mock_message.call_count == 4
    mock_time.sleep.assert_called_with(2)
    mock_gtts.assert_called()
    mock_st.audio.assert_called()

def test_show_messages_batch(mock_message, mock_time, mock_gtts, mock_st):
    """
    Test the show_messages function with batch mode enabled.
    
    Args:
        mock_message (Mock): The mocked Streamlit message function.
        mock_time (Mock): The mocked time.sleep function.
        mock_gtts (Mock): The mocked gTTS class.
        mock_st (Mock): The mocked Streamlit session state.
    
    Returns:
        None
    """
    mesg_1 = {
        "role": "Customer",
        "content": "Hello",
        "translation": "Hola",
        "language": "Spanish"
    }
    mesg_2 = {
        "role": "Waitstaff",
        "content": "How can I help you?",
        "translation": "¿Cómo puedo ayudarte?",
        "language": "Spanish"
    }
    
    new_counter = show_messages(mesg_1, mesg_2, 0, 2, batch=True, audio=False, translation=True)
    
    assert new_counter == 4
    assert mock_message.call_count == 4
    mock_time.sleep.assert_not_called()
    mock_gtts.assert_not_called()
    mock_st.audio.assert_not_called()