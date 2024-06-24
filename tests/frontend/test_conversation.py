import pytest
from unittest import mock
from frontend.src.conversation import generate_conversation, setup_conversation
import streamlit as st

def test_generate_conversation(mock_backend_server):
    """
    Test the generate_conversation function.

    Args:
        mock_backend_server (fixture): Mocked backend server fixture.
    """
    result = generate_conversation(
        role_dict={'role1': {'name': 'Customer'}, 'role2': {'name': 'Waitstaff'}},
        language="English",
        scenario="at a restaurant",
        proficiency_level="Beginner",
        learning_mode="Conversation",
        session_length="Short"
    )
    
    # Assert that the result is not None and contains expected responses
    assert result is not None
    assert result["response1"] == "Hello"
    assert result["response2"] == "Hi there"

def test_setup_conversation(mock_backend_server, mock_streamlit):
    """
    Test the setup_conversation function.

    Args:
        mock_backend_server (fixture): Mocked backend server fixture.
        mock_streamlit (fixture): Mocked Streamlit fixture.
    """
    mock_container, mock_column, mock_session_state = mock_streamlit
    conversation_container = mock_container.return_value
    translate_col, original_col, audio_col = st.columns(3)

    # Clear the session state before the test
    mock_session_state.clear()

    # Ensure session state keys are set
    mock_session_state['dual_chatbots'] = False
    mock_session_state['bot1_mesg'] = []
    mock_session_state['bot2_mesg'] = []
    mock_session_state['message_counter'] = 0
    mock_session_state['first_time_exec'] = True

    # Mock the sidebar button click
    with mock.patch('streamlit.sidebar.button', return_value=True):
        # Mock the generate_conversation function
        with mock.patch('frontend.src.conversation.generate_conversation', return_value={
            "response1": "Hello",
            "response2": "Hi there",
            "translate1": "Hello",
            "translate2": "Hi there"
        }):
            setup_conversation(
                conversation_container, translate_col, original_col, audio_col,
                "Conversation",
                {'role1': {'name': 'Customer'}, 'role2': {'name': 'Waitstaff'}},
                "English", "at a restaurant", "Beginner", "Short", 2
            )

    # Debug output to check session state
    print(mock_session_state)

    # Assertions to verify session state
    assert 'dual_chatbots' in mock_session_state
    assert 'bot1_mesg' in mock_session_state
    assert 'bot2_mesg' in mock_session_state
    assert 'message_counter' in mock_session_state
    assert 'first_time_exec' in mock_session_state
    assert mock_session_state['dual_chatbots'] is True
    assert isinstance(mock_session_state['bot1_mesg'], list)
    assert isinstance(mock_session_state['bot2_mesg'], list)
    assert mock_session_state['first_time_exec'] is False
