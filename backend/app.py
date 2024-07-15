import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.chatbot import DualChatbot

app = FastAPI()
# Use the llamafile server URL
LLM_SERVER = os.environ.get('LLM_SERVER', 'http://localhost:8080')

class ConversationRequest(BaseModel):
    """
    Pydantic model to define the request schema for conversation generation.
    
    Attributes:
        engine (str): The type of engine to use for the chatbots.
        role_dict (dict): The dictionary containing the roles for each chatbot.
        language (str): The language of the conversation.
        scenario (str): The scenario of the conversation.
        proficiency_level (str): The proficiency level of the language learner.
        learning_mode (str): The learning mode ('Conversation' or 'Debate').
        session_length (str): The length of the session ('Short' or 'Long').
    """
    engine: str
    role_dict: dict
    language: str
    scenario: str
    proficiency_level: str
    learning_mode: str
    session_length: str

class ConversationResponse(BaseModel):
    """
    Pydantic model to define the response schema for conversation generation.
    
    Attributes:
        response1 (str): The response from the first chatbot.
        response2 (str): The response from the second chatbot.
        translate1 (str): The translation of the first response.
        translate2 (str): The translation of the second response.
    """
    response1: str
    response2: str
    translate1: str
    translate2: str

# Global variable to store the DualChatbot instance
dual_chatbot = None

@app.post("/generate_conversation", response_model=ConversationResponse)
async def generate_conversation(request: ConversationRequest):
    """
    Endpoint to generate a conversation based on the provided request parameters.

    Args:
        request (ConversationRequest): The request parameters for generating the conversation.

    Returns:
        ConversationResponse: The responses and translations from both chatbots.

    Raises:
        HTTPException: If there is an error during the conversation generation.
    """
    global dual_chatbot
    try:
        if dual_chatbot is None:
            dual_chatbot = DualChatbot(
                request.engine,
                request.role_dict,
                request.language,
                request.scenario,
                request.proficiency_level,
                request.learning_mode,
                request.session_length,
                llm_server=LLM_SERVER
            )
        response1, response2, translate1, translate2 = dual_chatbot.step()
        return ConversationResponse(
            response1=response1,
            response2=response2,
            translate1=translate1,
            translate2=translate2
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_summary")
async def generate_summary(request: ConversationRequest):
    """
    Endpoint to generate a summary of the conversation.

    Args:
        request (ConversationRequest): The request parameters for generating the summary.

    Returns:
        dict: A dictionary containing the summary of the conversation.

    Raises:
        HTTPException: If no conversation has been generated or if there is an error during the summary generation.
    """
    global dual_chatbot
    try:
        if dual_chatbot is None:
            raise HTTPException(status_code=400, detail="No conversation has been generated yet.")
        summary = dual_chatbot.summary()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset_conversation")
async def reset_conversation():
    """
    Endpoint to reset the conversation history.

    Returns:
        dict: A message indicating that the conversation has been reset.
    """
    global dual_chatbot
    dual_chatbot = None
    return {"message": "Conversation reset successfully"}
