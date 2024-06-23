import pytest
from unittest.mock import Mock, patch
from src.conversation import setup_conversation

@pytest.fixture
def mock_st():
    with patch('src.conversation.st') as mock:
        mock.session_state = {}
        yield mock

@pytest.fixture
def mock_dual_chatbot():
    with patch('src.conversation.DualChatbot') as mock:
        yield mock

@pytest.fixture
def mock_show_messages():
    with patch('src.conversation.show_messages') as mock:
        yield mock

def test_setup_conversation_initial(mock_st, mock_dual_chatbot, mock_show_messages):
    mock_st.sidebar.button.return_value = True
    
    conversation_container = Mock()
    conversation_container.__enter__ = Mock()
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
    mock_dual_chatbot.assert_called_once()
    conversation_container.write.assert_called()

def test_setup_conversation_existing(mock_st, mock_dual_chatbot, mock_show_messages):
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
    
    conversation_container.write.assert_called()
    assert 'summary' in mock_st.session_state