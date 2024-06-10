import pytest
from src.chatbot import Chatbot, DualChatbot
from io import BytesIO

@pytest.fixture
def chatbot():
    return Chatbot(engine="OpenAI")

@pytest.fixture
def dual_chatbot():
    role_dict = {
        'role1': {'name': 'Customer', 'action': 'ordering food'},
        'role2': {'name': 'Waitstaff', 'action': 'taking the order'}
    }
    return DualChatbot(engine="OpenAI", role_dict=role_dict, language="Hindi", scenario="at a restaurant", 
                       proficiency_level="Beginner", learning_mode="Conversation", session_length="Short")

def test_instruct(chatbot):
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi", "at a restaurant", "Short", "Beginner", "Conversation")
    assert chatbot.language == "Hindi"
    assert chatbot.proficiency_level == "Beginner"

def test_generate_response(chatbot):
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi", "at a restaurant", "Short", "Beginner", "Conversation")
    response = chatbot.generate_response("Hello")
    assert isinstance(response, str)

def test_translate(chatbot):
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi", "at a restaurant", "Short", "Beginner", "Conversation")
    translation = chatbot.translate("नमस्ते")
    assert isinstance(translation, str)

def test_text_to_speech(chatbot):
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi", "at a restaurant", "Short", "Beginner", "Conversation")
    speech = chatbot.text_to_speech("नमस्ते")
    assert isinstance(speech, BytesIO)

def test_summary(dual_chatbot):
    summary = dual_chatbot.summary()
    assert isinstance(summary, str)
