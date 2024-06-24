import pytest
from unittest import mock
from frontend.src.utils import show_messages, initialize_session_state
from io import BytesIO
import streamlit as st

def test_initialize_session_state(mock_streamlit):
    """
    Test the initialize_session_state function to ensure it sets up the session state correctly.

    Args:
        mock_streamlit (fixture): Mocked Streamlit fixture.
    """
    mock_container, mock_column, mock_session_state = mock_streamlit
    initialize_session_state()
    
    # Assert that the session state contains the required keys
    assert "bot1_mesg" in mock_session_state
    assert "bot2_mesg" in mock_session_state
    assert "batch_flag" in mock_session_state
    assert "translate_flag" in mock_session_state
    assert "audio_flag" in mock_session_state
    assert "message_counter" in mock_session_state

def test_show_messages(mock_streamlit):
    """
    Test the show_messages function to ensure it displays messages correctly.

    Args:
        mock_streamlit (fixture): Mocked Streamlit fixture.
    """
    mock_container, mock_column, mock_session_state = mock_streamlit
    mock_session_state["message_counter"] = 0
    
    mesg_1 = {"role": "Customer", "content": "नमस्ते", "translation": "Hello", "language": "Hindi"}
    mesg_2 = {"role": "Waitstaff", "content": "स्वागत है", "translation": "Welcome", "language": "Hindi"}
    
    # Call show_messages and capture the message counter
    message_counter = show_messages(
        mesg_1, mesg_2, message_counter=0, time_delay=0, batch=True, audio=False, translation=False
    )
    
    # Assert that the message counter is updated correctly
    assert isinstance(message_counter, int)
    assert message_counter == 2

def test_text_to_speech():
    """
    Test the text_to_speech function to ensure it converts text to speech correctly.

    """
    with mock.patch('frontend.src.utils.gTTS') as mock_gtts:
        mock_gtts.return_value.write_to_fp.return_value = None
        from frontend.src.utils import text_to_speech
        
        # Call text_to_speech and capture the result
        result = text_to_speech("Hello", "en")
        
        # Assert that the result is a BytesIO object
        assert isinstance(result, BytesIO)
        mock_gtts.assert_called_once_with(text="Hello", lang="en")
