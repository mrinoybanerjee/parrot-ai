"""Tests for the conversation module."""

from unittest.mock import Mock, patch
import pytest
from src.conversation import setup_conversation

@pytest.fixture
def mock_st():
    """Mock the Streamlit session state."""
    with patch('src.conversation.st') as mock:
        mock.session_state = {}
        yield mock

@pytest.fixture
def mock_dual_chatbot():
    """Mock the DualChatbot class."""
    with patch('src.conversation.DualChatbot') as mock:
        yield mock

@pytest.fixture
def mock_show_messages():
    """Mock the show_messages function."""
    with patch('src.conversation.show_messages') as mock:
        yield mock

def test_setup_conversation_initial(mock_st, mock_dual_chatbot, mock_show_messages):
    """
    Test the setup_conversation function when the conversation is initialized for the first time.
    
    Args:
        mock_st (Mock): The mocked Streamlit session state.
        mock_dual_chatbot (Mock): The mocked DualChatbot class.
        mock_show_messages (Mock): The mocked show_messages function.
        
    Returns:
        None
    """
    mock_st.session_state = {}
    mock_st.sidebar.button.return_value = True  # Simulate 'Generate' button click
    
    conversation_container = Mock()
    # Instead of mocking __enter__, we'll mock the context manager itself
    conversation_container.__enter__ = Mock(return_value=conversation_container)
    conversation_container.__exit__ = Mock()
    translate_col = Mock()
    original_col = Mock()
    audio_col = Mock()
    
    setup_conversation(
        conversation_container, translate_col, original_col, audio_col,
        'Conversation', {'role1': {'name': 'Customer'}, 'role2': {'name': 'Waitstaff'}},
        'English', 'at a restaurant', 'Intermediate', 'Short', 2
    )
    
    assert 'dual_chatbots' in mock_st.session_state
    assert 'bot1_mesg' in mock_st.session_state
    assert 'bot2_mesg' in mock_st.session_state
    assert 'message_counter' in mock_st.session_state
    mock_dual_chatbot.assert_called_once()
    conversation_container.write.assert_called()

def test_setup_conversation_existing(mock_st, mock_dual_chatbot, mock_show_messages):
    """
    Test the setup_conversation function when the conversation is already initialized.
    
    Args:
        mock_st (Mock): The mocked Streamlit session state.
        mock_dual_chatbot (Mock): The mocked DualChatbot class.
        mock_show_messages (Mock): The mocked show_messages function.
    
    Returns:
        None
    """
    mock_st.session_state = {
        'dual_chatbots': Mock(),
        'bot1_mesg': [],
        'bot2_mesg': [],
        'first_time_exec': False,
        'batch_flag': False,
        'audio_flag': False,
        'translate_flag': False,
    }
    
    conversation_container = Mock()
    conversation_container.__enter__ = Mock()
    conversation_container.__exit__ = Mock()
    translate_col = Mock()
    original_col = Mock()
    audio_col = Mock()
    
    setup_conversation(
        conversation_container, translate_col, original_col, audio_col,
        'Debate', {'role1': {'name': 'Proponent'}, 'role2': {'name': 'Opponent'}},
        'Spanish', 'Climate change', 'Advanced', 'Long', 5
    )
    
    assert 'bot1_mesg' in mock_st.session_state
    assert 'bot2_mesg' in mock_st.session_state
