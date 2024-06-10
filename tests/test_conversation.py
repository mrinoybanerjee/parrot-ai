import pytest
from src.chatbot import DualChatbot

@pytest.fixture
def dual_chatbot():
    role_dict = {
        'role1': {'name': 'Customer', 'action': 'ordering food'},
        'role2': {'name': 'Waitstaff', 'action': 'taking the order'}
    }
    return DualChatbot(engine="OpenAI", role_dict=role_dict, language="Hindi", scenario="at a restaurant", 
                       proficiency_level="Beginner", learning_mode="Conversation", session_length="Short")

def test_dual_chatbot_initialization(dual_chatbot):
    assert dual_chatbot.language == "Hindi"
    assert dual_chatbot.proficiency_level == "Beginner"
    assert dual_chatbot.session_length == "Short"
