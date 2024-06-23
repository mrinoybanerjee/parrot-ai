import pytest
from unittest.mock import Mock, patch
from src.chatbot import Chatbot, DualChatbot

@pytest.fixture
def mock_openai():
    with patch('src.chatbot.OpenAI') as mock:
        yield mock

def test_chatbot_initialization(mock_openai):
    chatbot = Chatbot("OpenAI")
    assert chatbot.client is not None
    mock_openai.assert_called_once()

def test_chatbot_instruct():
    chatbot = Chatbot("OpenAI")
    chatbot.instruct(
        role={"name": "Customer", "action": "ordering food"},
        oppo_role={"name": "Waitstaff", "action": "taking the order"},
        language="English",
        scenario="at a restaurant",
        session_length="Short",
        proficiency_level="Intermediate",
        learning_mode="Conversation",
        starter=True
    )
    assert chatbot.role == {"name": "Customer", "action": "ordering food"}
    assert chatbot.language == "English"
    assert chatbot.prompt is not None

def test_chatbot_generate_response(mock_openai):
    chatbot = Chatbot("OpenAI")
    chatbot.instruct(
        role={"name": "Customer", "action": "ordering food"},
        oppo_role={"name": "Waitstaff", "action": "taking the order"},
        language="English",
        scenario="at a restaurant",
        session_length="Short",
        proficiency_level="Intermediate",
        learning_mode="Conversation",
        starter=True
    )
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response</s>"))]
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    response = chatbot.generate_response("Test input")
    assert response == "Test response"
    mock_openai.return_value.chat.completions.create.assert_called_once()

def test_chatbot_step():
    chatbot = Chatbot("OpenAI")
    chatbot.instruct(
        role={"name": "Customer", "action": "ordering food"},
        oppo_role={"name": "Waitstaff", "action": "taking the order"},
        language="English",
        scenario="at a restaurant",
        session_length="Short",
        proficiency_level="Intermediate",
        learning_mode="Conversation",
        starter=True
    )
    chatbot.generate_response = Mock(return_value="Response")
    chatbot.translate = Mock(return_value="Translation")

    response, translate = chatbot.step("Test input")
    assert response == "Response"
    assert translate == "Translation"

def test_dual_chatbot_initialization():
    role_dict = {
        "role1": {"name": "Customer", "action": "ordering food"},
        "role2": {"name": "Waitstaff", "action": "taking the order"}
    }
    dual_chatbot = DualChatbot(
        "OpenAI",
        role_dict,
        "English",
        "at a restaurant",
        "Intermediate",
        "Conversation",
        "Short"
    )
    assert dual_chatbot.chatbots["role1"]["chatbot"] is not None
    assert dual_chatbot.chatbots["role2"]["chatbot"] is not None
    assert dual_chatbot.language == "English"

def test_dual_chatbot_step():
    role_dict = {
        "role1": {"name": "Customer", "action": "ordering food"},
        "role2": {"name": "Waitstaff", "action": "taking the order"}
    }
    dual_chatbot = DualChatbot(
        "OpenAI",
        role_dict,
        "English",
        "at a restaurant",
        "Intermediate",
        "Conversation",
        "Short"
    )
    dual_chatbot.chatbots["role1"]["chatbot"].step = Mock(return_value=("Response 1", "Translation 1"))
    dual_chatbot.chatbots["role2"]["chatbot"].step = Mock(return_value=("Response 2", "Translation 2"))

    response1, response2, translate1, translate2 = dual_chatbot.step()
    assert response1 == "Response 1"
    assert response2 == "Response 2"
    assert translate1 == "Translation 1"
    assert translate2 == "Translation 2"