""" Tests for the Chatbot and DualChatbot classes. """

from io import BytesIO
import pytest
from unittest import mock
from backend.src.chatbot import Chatbot, DualChatbot


@pytest.fixture
def chatbot(mock_llm_server):
    """
    Fixture for creating a Chatbot instance with mocked OpenAI responses.

    Args:
        mock_llm_server (fixture): Mocked LLM server fixture.

    Returns:
        Chatbot: An instance of the Chatbot class with OpenAI mocked.
    """
    with mock.patch('backend.src.chatbot.OpenAI') as mock_openai:
        (mock_openai.return_value.chat.completions.create
         .return_value.choices[0].message.content) = "Mocked LLM response"
        return Chatbot(engine="OpenAI", llm_server="http://mock-llm-server")


@pytest.fixture
def dual_chatbot(mock_llm_server):
    """
    Fixture for creating a DualChatbot instance with mocked OpenAI responses.

    Args:
        mock_llm_server (fixture): Mocked LLM server fixture.

    Returns:
        DualChatbot: An instance of the DualChatbot class with OpenAI mocked.
    """
    with mock.patch('backend.src.chatbot.OpenAI') as mock_openai:
        (mock_openai.return_value.chat.completions.create
         .return_value.choices[0].message.content) = "Mocked LLM response"
        role_dict = {
            'role1': {'name': 'Customer', 'action': 'ordering food'},
            'role2': {'name': 'Waitstaff', 'action': 'taking the order'}
        }
        return DualChatbot(
            engine="OpenAI",
            role_dict=role_dict,
            language="Hindi",
            scenario="at a restaurant",
            proficiency_level="Beginner",
            learning_mode="Conversation",
            session_length="Short",
            llm_server="http://mock-llm-server"
        )


def test_instruct(chatbot):
    """
    Test the instruct method of the Chatbot class.

    Args:
        chatbot (Chatbot): The Chatbot instance to test.
    """
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi",
                     "at a restaurant", "Short", "Beginner", "Conversation")
    assert chatbot.language == "Hindi"
    assert chatbot.proficiency_level == "Beginner"


def test_generate_response(chatbot):
    """
    Test the generate_response method of the Chatbot class.

    Args:
        chatbot (Chatbot): The Chatbot instance to test.
    """
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi",
                     "at a restaurant", "Short", "Beginner", "Conversation")
    response = chatbot.generate_response("Hello")
    assert response == "Mocked LLM response"


def test_translate(chatbot):
    """
    Test the translate method of the Chatbot class.

    Args:
        chatbot (Chatbot): The Chatbot instance to test.
    """
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi",
                     "at a restaurant", "Short", "Beginner", "Conversation")
    translation = chatbot.translate("नमस्ते")
    assert translation == "Mocked LLM response"


def test_text_to_speech(chatbot, mock_llm_server):
    """
    Test the text_to_speech method of the Chatbot class.

    Args:
        chatbot (Chatbot): The Chatbot instance to test.
        mock_llm_server (fixture): Mocked LLM server fixture.
    """
    role = {'name': 'Customer', 'action': 'ordering food'}
    oppo_role = {'name': 'Waitstaff', 'action': 'taking the order'}
    chatbot.instruct(role, oppo_role, "Hindi",
                     "at a restaurant", "Short", "Beginner", "Conversation")
    speech = chatbot.text_to_speech("नमस्ते")
    assert isinstance(speech, BytesIO)


def test_summary(dual_chatbot):
    """
    Test the summary method of the DualChatbot class.

    Args:
        dual_chatbot (DualChatbot): The DualChatbot instance to test.
    """
    summary = dual_chatbot.summary()
    assert summary == "Mocked LLM response"


def test_dual_chatbot_step(dual_chatbot):
    """
    Test the step method of the DualChatbot class.

    Args:
        dual_chatbot (DualChatbot): The DualChatbot instance to test.
    """
    response1, response2, translate1, translate2 = dual_chatbot.step()
    assert all(item == "Mocked LLM response" for item in [response1, response2,
                                                          translate1, translate2])
