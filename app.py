import streamlit as st
import os
import requests
import json
from datetime import datetime
from src.conversation import setup_conversation
from src.utils import initialize_session_state

LLM_SERVER = os.environ.get('LLM_SERVER', 'http://localhost:8080')

def check_llm_server():
    """Check if the LLM server is running."""
    try:
        response = requests.get(f"{LLM_SERVER}/v1/models", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
    
st.set_page_config(page_title="Parrot-AI", page_icon="🦜")

# Set the title of the app
st.title('Parrot-AI 🦜🌍')

# Set the description of the app
st.markdown("""
This app generates conversation or debate scripts to aid in language learning 🎯

Choose your desired settings and press 'Generate' to start 🚀
""")

if not check_llm_server():
    st.error("LLM server is not running. Please start the LLM server before using Parrot-AI.")
    st.info("Run the following command in your terminal to start the LLM server:")
    st.code("./mistral-7b-instruct-v0.2.Q4_0.llamafile --server --host 0.0.0.0 --port 8080")
    st.stop()

# Define the language learning settings
LANGUAGES = ['English', 'Hindi', 'German', 'Spanish', 'French']
SESSION_LENGTHS = ['Short', 'Long']
PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']

# Add a selectbox for learning mode
learning_mode = st.sidebar.selectbox('Learning Mode 📖', ('Conversation', 'Debate'))

if learning_mode == 'Conversation':
    role1 = st.sidebar.text_input('Role 1 🎭', 'Customer')
    action1 = st.sidebar.text_input('Action 1 🗣️', 'ordering food')
    role2 = st.sidebar.text_input('Role 2 🎭', 'Waitstaff')
    action2 = st.sidebar.text_input('Action 2 🗣️', 'taking the order')
    scenario = st.sidebar.text_input('Scenario 🎥', 'at a restaurant')
    time_delay = 2

    # Configure role dictionary
    role_dict = {
        'role1': {'name': role1, 'action': action1},
        'role2': {'name': role2, 'action': action2}
    }

else:
    scenario = st.sidebar.text_input('Debate Topic 💬', 'Climate change')

    # Configure role dictionary
    role_dict = {
        'role1': {'name': 'Proponent'},
        'role2': {'name': 'Opponent'}
    }
    time_delay = 5

language = st.sidebar.selectbox('Target Language 🔤', LANGUAGES)
session_length = st.sidebar.selectbox('Session Length ⏰', SESSION_LENGTHS)
proficiency_level = st.sidebar.selectbox('Proficiency Level 🏆', PROFICIENCY_LEVELS)

# Initialize session states
initialize_session_state()

# Define the button layout at the beginning
translate_col, original_col, audio_col = st.columns(3)

# Create the conversation container
conversation_container = st.container()

setup_conversation(conversation_container, translate_col, original_col, audio_col, learning_mode,
                   role_dict, language, scenario, proficiency_level, session_length, time_delay)