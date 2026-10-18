""" Tests for the conversation module. """

from unittest import mock
import streamlit as st
from frontend.src.conversation import generate_conversation, setup_conversation


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
    mock_session_state['summary'] = 'Stale previous learning points'

    # Mock the sidebar button click
    with mock.patch('streamlit.sidebar.button', return_value=True):
        # Mock the generate_conversation function
        with mock.patch('frontend.src.conversation.generate_conversation',
                        return_value={
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
    assert mock_session_state['summary'] == 'This is a summary'


def test_reset_connection_failure_is_shown(mock_streamlit):
    import requests
    from frontend.src import conversation

    container, column, state = mock_streamlit
    state['summary'] = 'Previous learning points'
    with mock.patch('streamlit.sidebar.button', return_value=True), \
            mock.patch.object(conversation.requests, 'post', side_effect=requests.ConnectionError), \
            mock.patch('streamlit.error') as error:
        conversation.setup_conversation(container, column, column, column, 'Conversation', {},
                                        'English', 'cafe', 'Beginner', 'Short', 0)
    error.assert_called_once()
    assert state['summary'] == 'Previous learning points'


def test_session_header_is_stable_and_random_per_browser(mock_streamlit):
    from frontend.src.conversation import session_headers

    _, _, state = mock_streamlit
    first = session_headers()
    assert session_headers() == first
    assert len(first['X-Session-ID']) == 32
    state.clear()
    assert session_headers() != first


def test_failed_step_keeps_partial_history_visible_on_rerun(mock_backend_server, mock_streamlit):
    from frontend.src import conversation
    from frontend.src.utils import initialize_session_state

    container, column, state = mock_streamlit
    initialize_session_state()
    exchange = dict(response1='Hello', response2='Hi', translate1='Hello', translate2='Hi')
    with mock.patch('streamlit.sidebar.button', return_value=True), \
            mock.patch.object(conversation, 'generate_conversation', side_effect=[exchange, None]):
        conversation.setup_conversation(container, column, column, column, 'Conversation',
            {'role1': {'name': 'A'}, 'role2': {'name': 'B'}}, 'English', 'cafe', 'Beginner', 'Short', 0)
    assert state['first_time_exec'] is False
    assert len(state['bot1_mesg']) == len(state['bot2_mesg']) == 1


def test_conversation_timeout_covers_four_sequential_model_calls(mock_streamlit):
    from frontend.src import conversation

    with mock.patch.object(conversation.requests, 'post') as post:
        conversation.generate_conversation({}, 'Spanish', 'cafe', 'Beginner', 'Conversation', 'Short')
    assert post.call_args.kwargs['timeout'][1] > 4 * 120 + 5
